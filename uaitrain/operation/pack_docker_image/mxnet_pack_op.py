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

from uaitrain.operation.pack_docker_image.base_pack_op import BaseUAITrainDockerImagePackOp

class MXNetUAITrainDockerImagePackOp(BaseUAITrainDockerImagePackOp):
    """docstring for ClassName"""
    def __init__(self, parser):
        super(MXNetUAITrainDockerImagePackOp, self).__init__(parser)
        self.ai_arch = "caffe"

    def _parse_args(self, args):
        super(MXNetUAITrainDockerImagePackOp, self)._parse_args(args)

    def _add_args(self):
        super(MXNetUAITrainDockerImagePackOp, self)._add_args()

    def _gen_gpu_docker_cmd(self, pycmd):
        gpu_docker_cmd = "sudo nvidia-docker run -it " + \
            "-v " + self.test_data_path + ":" + "/data/data " + \
            "-v " + self.test_output_path + ":" + "/data/output " + \
            self.user_gpu_image + " " + "/bin/bash -c " + \
            "\"cd /data && /usr/bin/python " + pycmd + " " + "--num_gpus=1 --work_dir=/data --data_dir=/data/data --output_dir=/data/output --log_dir=/data/output\""
        return gpu_docker_cmd


        