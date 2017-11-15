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

import argparse

from uaitrain.operation.pack_docker_image.caffe_pack_op import CaffeUAITrainDockerImagePackOp
from uaitrain.operation.create_train_job.base_create_op import BaseUAITrainCreateTrainJobOp
from uaitrain.operation.stop_train_job.base_stop_op import BaseUAITrainStopTrainJobOp
from uaitrain.operation.delete_train_job.base_delete_op import BaseUAITrainDeleteTrainJobOp
from uaitrain.operation.list_train_job.base_list_job_op import BaseUAITrainListTrainJobOp
from uaitrain.operation.info_train_job.info_train_op import BaseUAITrainRunningJobInfoOp
from uaitrain.operation.get_realtime_log.base_log_op import BaseUAITrainGetRealtimeLogOp
from uaitrain.operation.list_bill_info.base_bill_op import BaseUAITrainListBillInfoOp
from uaitrain.operation.rename_train_job.base_rename_op import BaseUAITrainRenameTrainJobOp
from uaitrain.operation.get_train_job_conf.base_conf_op import BaseUAITrainTrainJobConfOp

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='AI Caffe Arch Deployer',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    subparsers = parser.add_subparsers(dest='commands', help='commands')

    pack_op = CaffeUAITrainDockerImagePackOp(subparsers)
    create_op = BaseUAITrainCreateTrainJobOp(subparsers)
    stop_op = BaseUAITrainStopTrainJobOp(subparsers)
    delete_op = BaseUAITrainDeleteTrainJobOp(subparsers)
    list_op = BaseUAITrainListTrainJobOp(subparsers)
    info_op = BaseUAITrainRunningJobInfoOp(subparsers)
    log_op = BaseUAITrainGetRealtimeLogOp(subparsers)
    bill_op = BaseUAITrainListBillInfoOp(subparsers)
    rename_op = BaseUAITrainRenameTrainJobOp(subparsers)
    conf_op = BaseUAITrainTrainJobConfOp(subparsers)
    cmd_args = vars(parser.parse_args())

    if cmd_args['commands'] == 'pack':
        pack_op.cmd_run(cmd_args)
    elif cmd_args['commands'] == 'create':
        create_op.cmd_run(cmd_args)
    elif cmd_args['commands'] == 'stop':
        stop_op.cmd_run(cmd_args)
    elif cmd_args['commands'] == 'delete':
        delete_op.cmd_run(cmd_args)
    elif cmd_args['commands'] == 'list':
        list_op.cmd_run(cmd_args)
    elif cmd_args['commands'] == 'info':
        info_op.cmd_run(cmd_args)
    elif cmd_args['commands'] == 'log':
        log_op.cmd_run(cmd_args)
    elif cmd_args['commands'] == 'bill':
        bill_op.cmd_run(cmd_args)
    elif cmd_args['commands'] == 'rename':
        rename_op.cmd_run(cmd_args)
    elif cmd_args['commands'] == 'conf':
        conf_op.cmd_run(cmd_args)

    else:
        print("Unknown CMD, please use python caffe_tool.py -h to check")

