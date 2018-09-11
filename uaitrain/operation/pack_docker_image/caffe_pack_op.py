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


class CaffeUAITrainDockerImagePackOp(BaseUAITrainDockerImagePackOp):
    def __init__(self, parser):
        super(CaffeUAITrainDockerImagePackOp, self).__init__(parser)
        self.ai_arch = "caffe"

    def _add_caffe_run_args(self, pack_parser):
        caffe_parse = pack_parser.add_argument_group(
            'Caffe_params', 'Caffe specific params, used to identify xxx.prototxt files')
        caffe_parse.add_argument(
            '--solver',
            type=str,
            required=True,
            help='solver prototxt file name, related path to solver file considering code_path as root')
        caffe_parse.add_argument(
            '--snapshot',
            type=str,
            help="Solver snapshot to restore")

    def _parse_args(self, args):
        super(CaffeUAITrainDockerImagePackOp, self)._parse_args(args)

        self.solver = args['solver']
        self.snapshot = args['snapshot']

    def _add_args(self):
        super(CaffeUAITrainDockerImagePackOp, self)._add_args()
        self._add_caffe_run_args(self.pack_parser) 

    def _gen_pycmd(self):
        pycmd = "/data/" + self.mainfile_path + " " + "--solver=" + self.solver
        if self.snapshot != None and self.snapshot != "":
            pycmd = pycmd + " --snapshot=" + self.snapshot
        return pycmd

    def _gen_cpu_docker_cmd(self, pycmd):
        cpu_docker_cmd = "sudo docker run -it " + \
            "-v " + self.test_data_path + ":" + "/data/data " + \
            "-v " + self.test_output_path + ":" + "/data/output " + \
            self.user_cpu_image + " " + "/bin/bash -c " + \
            "\"cd /data && /usr/bin/python " + pycmd + " " + "--use_cpu=True --work_dir=/data --data_dir=/data/data --output_dir=/data/output --log_dir=/data/output\" "
        return cpu_docker_cmd

    def _gen_gpu_docker_cmd(self, pycmd):
        gpu_docker_cmd = "sudo nvidia-docker run -it " + \
            "-v " + self.test_data_path + ":" + "/data/data " + \
            "-v " + self.test_output_path + ":" + "/data/output " + \
            self.user_gpu_image + " " + "/bin/bash -c " + \
            "\"cd /data && /usr/bin/python " + pycmd + " " + "--use_cpu=False --num_gpus=1 --work_dir=/data --data_dir=/data/data --output_dir=/data/output --log_dir=/data/output\""
        return gpu_docker_cmd
