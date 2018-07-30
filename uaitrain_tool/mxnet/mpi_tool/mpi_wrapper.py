from __future__ import absolute_import
from __future__ import print_function

import argparse
import os
import sys
import subprocess, logging
from threading import Thread

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

def mpi_submit(role, nworker, nserver, args, pass_envs):
    """Internal closure for job submission."""
    def run(prog):
        """run the program"""
        subprocess.check_call(prog, shell=True)

    pass_envs['DMLC_JOB_CLUSTER'] = 'mpi'
    pass_envs['OMP_NUM_THREADS'] = 8
    if 'UAI_HOSTS' in pass_envs:
        hosts = pass_envs['UAI_HOSTS']
    else:
        hosts = None

    cmd =' '.join(args.command)
    if hosts is not None:
        print(hosts, file=sys.stderr)
        cmd += ' --uai-hosts %s ' % (hosts)
    print(cmd, file=sys.stderr)

    if role == 'server':
        print('Start servers by mpirun')
        prog = 'mpirun -n 1 --allow-run-as-root --map-by node  %s %s' % (get_mpi_env(pass_envs), cmd)
        print(prog, file=sys.stderr)
        thread = Thread(target=run, args=(prog,))
        thread.setDaemon(True)
        thread.start()
    else: # role is worker
        print('Start workers by mpirun')
        prog = 'mpirun -n 1 --allow-run-as-root --map-by node %s %s' % (get_mpi_env(pass_envs), cmd)
        print(prog, file=sys.stderr)
        thread = Thread(target=run, args=(prog,))
        thread.setDaemon(True)
        thread.start()
    while thread.isAlive():
        thread.join(100)

def run_tracker(cmd, env):
    print('Start scheduler')
    thread = Thread(target=(lambda: subprocess.check_call(cmd, env=env, shell=True)), args=())
    thread.setDaemon(True)
    thread.start()

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
        run_tracker(' '.join(args.command), env)
    else:
        mpi_submit(role, nworker, nserver, args, env)

if __name__ == "__main__":
    main()
