from __future__ import absolute_import
from __future__ import print_function

import argparse
import os
import sys
import string
import subprocess, logging
from threading import Thread

import time
import socket
import commands

def get_mpi_env(envs):
    """get the mpirun command for setting the envornment
    support both openmpi and mpich2
    """

    cmd = ''
    # windows hack: we will use msmpi
    if sys.platform == 'win32':
        for k, v in envs.items():
            cmd += ' -env %s %s' % (k, str(v))
        return cmd

    # decide MPI version.
    (out, err) = subprocess.Popen(['mpirun', '--version'],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE).communicate()
    if b'Open MPI' in out:
        for k, v in envs.items():
            if k == 'LS_COLORS':
                continue

            cmd += ' -x %s=%s' % (k, str(v))
    elif b'mpich' in err:
        for k, v in envs.items():
            cmd += ' -env %s %s' % (k, str(v))
    else:
        raise RuntimeError('Unknown MPI Version')
    return cmd

def mpi_submit(role, nworker, nserver, args, envs):
    """Internal closure for job submission."""
    def run(prog):
        """run the program"""
        subprocess.check_call(prog, shell=True)

    def notify_ready():
        master_ip = envs['DMLC_PS_ROOT_URI']
        master_port = 12345
        s = socket.socket()
        s.connect((master_ip, master_port))
        role = s.recv(128)
        print(role, file=sys.stderr)
        # close the connection

        if role == 'Master':
            progPs = s.recv(2048)
            progWk = s.recv(2048)
            print(progPs, file=sys.stderr)
            print(progWk, file=sys.stderr)
        else:
            progPs = ''
            progWk = ''
            s.close()
        return role, progPs, progWk

    if 'UAI_HOSTS' in envs:
        hosts = envs['UAI_HOSTS']
    else:
        sys.exit(1)
    print(hosts, file=sys.stderr)

    cmd =' '.join(args.command)
    if hosts is not None:
        host_list = string.split(hosts, ',')
        cmd += ' --uai-hosts %s ' % (hosts)
    else:
        sys.exit(1)

    if role == 'server':
        print('Bind to role=server', file=sys.stderr)
        port = 12346
        s = socket.socket() 
        s.bind(('', port))
        s.listen(5)
        c, addr = s.accept()
        c.close()

    else: # role is worker
        print(os.path.isdir('/data/data/'), file=sys.stderr)

        print('change /root/.ssh/config', file=sys.stderr)
        ssh_cmd = "sed -i 's/port 23/port 24/' /root/.ssh/config"
        subprocess.check_call(ssh_cmd, shell=True)

        prog = '/usr/sbin/sshd -D -p 24'
        print(prog, file=sys.stderr)
        thread = Thread(target=run, args=(prog,))
        thread.setDaemon(True)
        thread.start()

        time.sleep(1)
        while True:
            output = commands.getoutput('ps -A')
            print(output, file=sys.stderr)
            if 'sshd' in output:
                break
            time.sleep(1)

        role, progPs, progWk = notify_ready()
        if role == 'Master':
            print('Start servers by mpirun', file=sys.stderr)
            progPs = '%s  %s' % (progPs, cmd)
            print(progPs, file=sys.stderr)
            thread_ps_run = Thread(target=run, args=(progPs,))
            thread_ps_run.setDaemon(True)
            thread_ps_run.start()

            print('Start workers by mpirun', file=sys.stderr)
            progWk = '%s  %s' % (progWk, cmd)
            print(progWk, file=sys.stderr)
            thread_wk_run = Thread(target=run, args=(progWk,))
            thread_wk_run.setDaemon(True)
            thread_wk_run.start()

            while thread_wk_run.isAlive():
                thread_wk_run.join(120)
                thread_ps_run.join(120)
            print('Master worker exit', file=sys.stderr)
            sys.exit(0)
        else:
            while thread.isAlive():
                thread.join(120) 

    sys.exit(0)

def run_tracker(args, env):
    def run(prog):
        """run the program"""
        subprocess.check_call(prog, shell=True)

    print('Start scheduler', file=sys.stderr)
    thread = Thread(target=(lambda: subprocess.check_call(' '.join(args.command), env=env, shell=True)), args=())
    thread.setDaemon(True)
    thread.start()

    env['DMLC_JOB_CLUSTER'] = 'mpi'
    if 'UAI_HOSTS' in env:
        hosts = env['UAI_HOSTS']
    else:
        sys.exit(1)
    print(hosts, file=sys.stderr)

    cmd =' '.join(args.command)
    if hosts is not None:
        host_list = string.split(hosts, ',')
        cmd += ' --uai-hosts %s ' % (hosts)
    else:
        sys.exit(1)

    host_cnt = len(host_list)
    hosts = ','.join(sorted(host_list, reverse=True))  
    print(host_list, file=sys.stderr)
    print(hosts, file=sys.stderr)

    # start socket
    s = socket.socket()
    master_ip = env['DMLC_PS_ROOT_URI'] 
    port = 12345
    s.bind(('', port))
    print('socket bind %s' %(port), file=sys.stderr)
    s.listen(5)

    # Now check for worker docker start
    for x in xrange(host_cnt):
        c, addr = s.accept()
        print(addr, file=sys.stderr)
        if addr[0] == master_ip:
            c.send('Master')
            master_c = c
        else:
            c.send('Slave')
            c.close()

    env['OMP_NUM_THREADS'] = 4
    #env['MXNET_CPU_WORKER_NTHREADS'] = 8
    #env['MXNET_GPU_WORKER_NTHREADS'] = 4
    env['DMLC_ROLE'] = 'server'
    prog = 'mpirun --allow-run-as-root --mca btl_tcp_if_include eth1 --map-by socket -n %d -host %s %s' % (host_cnt, hosts, get_mpi_env(env))
    master_c.send(prog)

    env['DMLC_ROLE'] = 'worker'
    prog = 'mpirun --allow-run-as-root --mca btl_tcp_if_include eth1 --map-by socket -n %d -host %s %s' % (host_cnt, hosts, get_mpi_env(env))
    master_c.send(prog)
    master_c.close()

    while thread.isAlive():
        thread.join(100)

def main():
    parser = argparse.ArgumentParser(description='Launch a distributed job')
    parser.add_argument('--command', nargs='+',
                         help = 'command for launching the program')

    args, unknown = parser.parse_known_args()
    args.command += unknown

    env = os.environ.copy()
    role = env['DMLC_ROLE']
    nworker = env['DMLC_NUM_WORKER']
    nserver = env['DMLC_NUM_SERVER']
    print(args.command)
    if role == 'scheduler':
        run_tracker(args, env)
    else:
        mpi_submit(role, nworker, nserver, args, env)

if __name__ == "__main__":
    main()