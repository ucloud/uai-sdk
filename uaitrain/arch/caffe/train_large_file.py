#!/usr/bin/env python
# Copyright 2017 The UAI-SDK Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""
Trains a model using one or more GPUs.
"""
from multiprocessing import Process

import caffe
import os

def train(
        solver,  # solver proto definition
        snapshot,  # solver snapshot to restore
        use_cpu, #whether use cpu
        gpus,  # list of device ids
        timing=False,  # show timing info for compute and communications
):
    caffe.init_log(0,True)
    caffe.log('Using devices %s' % str(gpus))

    if use_cpu == True:
        p = Process(target=cpu_solve,
                    args=(solver, snapshot, timing))

        p.daemon = True
        p.start()
        p.join()
    else:
        # NCCL uses a uid to identify a session
        uid = caffe.NCCL.new_uid()

        procs = []
        for rank in range(len(gpus)):
            p = Process(target=solve,
                        args=(solver, snapshot, gpus, timing, uid, rank))
            p.daemon = True
            p.start()
            procs.append(p)
        for p in procs:
            p.join()

def time(solver, nccl):
    fprop = []
    bprop = []
    total = caffe.Timer()
    allrd = caffe.Timer()
    for _ in range(len(solver.net.layers)):
        fprop.append(caffe.Timer())
        bprop.append(caffe.Timer())
    display = solver.param.display

    def show_time():
        if solver.iter % display == 0:
            s = '\n'
            for i in range(len(solver.net.layers)):
                s += 'forw %3d %8s ' % (i, solver.net._layer_names[i])
                s += ': %.2f\n' % fprop[i].ms
            for i in range(len(solver.net.layers) - 1, -1, -1):
                s += 'back %3d %8s ' % (i, solver.net._layer_names[i])
                s += ': %.2f\n' % bprop[i].ms
            s += 'solver total: %.2f\n' % total.ms
            s += 'allreduce: %.2f\n' % allrd.ms
            caffe.log(s)

    solver.net.before_forward(lambda layer: fprop[layer].start())
    solver.net.after_forward(lambda layer: fprop[layer].stop())
    solver.net.before_backward(lambda layer: bprop[layer].start())
    solver.net.after_backward(lambda layer: bprop[layer].stop())
    solver.add_callback(lambda: total.start(), lambda: (total.stop(), allrd.start()))
    solver.add_callback(nccl)
    solver.add_callback(lambda: '', lambda: (allrd.stop(), show_time()))


def solve(proto, snapshot, gpus, timing, uid, rank):
    caffe.set_mode_gpu()
    caffe.set_device(gpus[rank])
    caffe.set_solver_count(len(gpus))
    caffe.set_solver_rank(rank)
    caffe.set_multiprocess(True)

    solver = caffe.SGDSolver(proto)
    if snapshot and len(snapshot) != 0:
        solver.restore(snapshot)

    nccl = caffe.NCCL(solver, uid)
    nccl.bcast()

    if timing and rank == 0:
        time(solver, nccl)
    else:
        solver.add_callback(nccl)

    if solver.param.layer_wise_reduce:
        solver.net.after_backward(nccl)
    solver.step(solver.param.max_iter)

def cpu_solve(proto, snapshot, timing):
    caffe.set_mode_cpu()

    solver = caffe.SGDSolver(proto)
    if snapshot and len(snapshot) != 0:
        solver.restore(snapshot)

    solver.step(solver.param.max_iter)

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def join(fromdir, fromfile, tofile):
    readsize = 1024
    parts  = os.listdir(fromdir)
    output = open(tofile, 'wb')
    parts.sort()
    for filename in parts:
        if filename.startswith(fromfile) is False:
            continue
        filepath = os.path.join(fromdir, filename)
        fileobj  = open(filepath, 'rb')
        while 1:
            filebytes = fileobj.read(readsize)
            if not filebytes: break
            output.write(filebytes)
        fileobj.close()
        os.remove(filepath)
    output.close()

def merge_data(args):
    if args.train_dir != "" and args.train_slice_name != "" and args.train_file_name != "":
        join(args.train_dir, args.train_slice_name, args.train_file_name)
        print("join train data")

    if args.val_dir != "" and args.val_slice_name != "" and args.val_file_name != "":
        join(args.val_dir, args.val_slice_name, args.val_file_name)
        print("join val data")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("--solver", required=True, help="Solver proto definition.")
    parser.add_argument("--snapshot", help="Solver snapshot to restore.")
    parser.add_argument("--use_cpu", type=str2bool, default=False, help="Use CPU?")
    parser.add_argument("--num_gpus", type=int, default=1, help="Num of GPUs")
    parser.add_argument("--timing", action='store_true', help="Show timing info.")
    parser.add_argument("--work_dir", help="No usage, compatable with other AI Archs")
    parser.add_argument("--data_dir", help="No usage, compatable with other AI Archs")
    parser.add_argument("--output_dir", help="No usage, compatable with other AI Archs")
    parser.add_argument("--log_dir", help="No usage, compatable with other AI Archs")
    parser.add_argument("--train_dir", type=str, default="", help="The dir containing train data slices to merge")
    parser.add_argument("--train_slice_name", type=str, default="", help="The train data slice prefix name")
    parser.add_argument("--train_file_name", type=str, default="", help="For train data filename after merge")
    parser.add_argument("--val_dir", type=str, default="", help="The dir containing evaluation data slices to merge")
    parser.add_argument("--val_slice_name", type=str, default="", help="The evaluation data slice prefix name")
    parser.add_argument("--val_file_name", type=str, default="", help="For evaluation data filename after merge")
    args = parser.parse_args()

    merge_data(args)

    num_gpus = args.num_gpus
    gpus = []
    for i in range(0, num_gpus):
        gpus.append(i)
    print(args.use_cpu)
    train(args.solver, args.snapshot, args.use_cpu, gpus, args.timing)
