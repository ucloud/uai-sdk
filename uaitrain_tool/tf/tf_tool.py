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

import sys
import os
import argparse
import time

from uaitrain.operation.pack_docker_image.tf_pack_op import TensorFlowUAITrainDockerImagePackOp

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='AI TensorFlow Arch Deployer',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    subparsers = parser.add_subparsers(dest='commands', help='commands')

    pack_op = TensorFlowUAITrainDockerImagePackOp(subparsers)
    cmd_args = vars(parser.parse_args())

    if cmd_args['commands'] == 'pack':
        pack_op.cmd_run(cmd_args)
    else:
        print("UAI Train Deploy Tool Only Support Packing Docker Images Now")
    
