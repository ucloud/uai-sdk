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

import subprocess

from uai.utils.logger import uai_logger
from uaitrain.operation.pack_docker_image.base_pack_op import BaseUAITrainDockerImagePackOp
from uaitrain.operation.pack_docker_image.base_pack_op import TMP_DOCKER_FILE
from uaitrain.operation.pack_docker_image.base_pack_op import DOCKER_RUN_CMD_FILE

class SelfDefUAITrainDockerImagePackOp(BaseUAITrainDockerImagePackOp):
    """docstring for ClassName"""
    def __init__(self, parser):
        super(SelfDefUAITrainDockerImagePackOp, self).__init__(parser)

    def _add_self_def_image(self, pack_parser):
        pack_parser.add_argument(
            '--self_img',
            type=str,
            required=False,
            default='',
            help='The self defined docker image name')

    def _add_args(self):
        super(SelfDefUAITrainDockerImagePackOp, self)._add_args()

        self._add_self_def_image(self.pack_parser)

    def _parse_args(self, args):
        super(SelfDefUAITrainDockerImagePackOp, self)._parse_args(args)

        if args['self_img'] == '':
            raise RuntimeError('Need self defined image name')
        self.base_image_name = args['self_img']

    def _build_gpu_userimage(self):
        '''
        Build actual image for training
        '''
        uai_logger.info("Build training docker image")
        uai_logger.info("Pull base image from " + self.base_image_name)
        retcode = subprocess.check_call(["docker", "pull", self.base_image_name],
                                        stderr=subprocess.STDOUT)
        if retcode != 0:
            raise RuntimeError("Error pull image: {0}, Please check your network".format(self.acc_image))

        uai_logger.info("Create GPU Dockerfile")
        dockerbuf = []
        dockerbuf.append("From " + self.base_image_name + "\n")
        dockerbuf.append("ADD " + "./" + self.code_path + " /data/\n")
        with open(TMP_DOCKER_FILE, 'w') as f:
            f.write(''.join(dockerbuf))

        uai_logger.info("Build user image")
        print(self.dcoker_register)
        userimage = self.dcoker_register + "/" + self.uhub_registry + "/" + self.uhub_imagename
        if self.uhub_imagetag != None and self.uhub_imagetag != "":
            userimage = userimage + ":" + self.uhub_imagetag
        else:
            userimage = userimage + ":" + DOCKER_TAG_SUFFIX
        retcode = subprocess.check_call(["docker", "build", "-t", userimage, "-f", TMP_DOCKER_FILE, "."],
                                        stderr=subprocess.STDOUT)
        if retcode != 0:
            raise RuntimeError("Error build image: {0}, Please retry".format(userimage))

        print(userimage)
        self.user_gpu_image = userimage

    def _gen_gpu_docker_cmd(self, pycmd):
        gpu_docker_cmd = "sudo nvidia-docker run -it " + \
            "-v " + self.test_data_path + ":" + "/data/data " + \
            "-v " + self.test_output_path + ":" + "/data/output " + \
            self.user_gpu_image + " " + "/bin/bash -c " + \
            "\"cd /data && /usr/bin/python " + pycmd + " " + "--num_gpus=1 --work_dir=/data --data_dir=/data/data --output_dir=/data/output --log_dir=/data/output\""
        return gpu_docker_cmd

    def _gen_run_cmd(self):
        f = open(DOCKER_RUN_CMD_FILE, "w")

        """ Python cmd used in deploy
        """
        pycmd = self._gen_pycmd()
        f.write("CMD Used for deploying: " + pycmd + "\n")
        print("CMD Used for deploying: {0}".format(pycmd))

        gpu_docker_cmd = self._gen_gpu_docker_cmd(pycmd)
        f.write("CMD for GPU local test: " + gpu_docker_cmd + "\n")
        print("CMD for GPU local test: {0}".format(gpu_docker_cmd))

        f.close()
        print("You can check these cmd later in file: {0}".format(DOCKER_RUN_CMD_FILE))

    def _build_userimage(self):
        self._build_gpu_userimage()
        self._gen_run_cmd()

    def cmd_run(self, args):
        if self._parse_args(args) == False:
            return False

        self._build_userimage()
        
        