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

import os 
import sys
import json
import argparse
import tarfile
import subprocess
from datetime import datetime
from uai.utils.logger import uai_logger
from uaitrain.cmd.base_cmd import UaiCmdTool


#DOCKER_REGISTRY = "uhub.service.ucloud.cn"
DOCKER_REGISTRY = "uhub.ucloud.cn"
DOCKER_TAG_SUFFIX = "uaitrain"
TMP_CPU_DOCKER_FILE = "uaitrain-cpu.Dockerfile"
TMP_DOCKER_FILE = "uaitrain.Dockerfile"
DOCKER_RUN_CMD_FILE = "uaitrain_cmd.txt"

class UaiPackTool(object):
    """ The Base Pack Tool Class with UAI
    """
    def __init__(self, platform, parser):
        self.platform = platform
        self.parser = parser

        self.conf_params = {}
        
        self._add_args()

    def _add_args(self):
        """ AI Arch Specific Pack Tool should implement its own _add_args
        """
        raise UserWarning("UaiPackTool._add_args Unimplemented")

    def _analysis_args(self):
        self.config.load_params()
        if self.config.params.has_key("ai_arch_v"):
            if self.platform != self.config.params["ai_arch_v"].lower().split('-')[0]:
                raise RuntimeError("ai_arch_v should be one version of " + self.platform)
        if self.config.params.has_key("accelerator"):
            self.accelerator = self.config.params["accelerator"]

    def _load_args(self):
        """ AI Arch Specific Pack Tool should implement its own _load_args
        """
        raise UserWarning("UaiPackTool._load_args Unimplemented")

    def _translate_args(self, params):
        # self.translateTool = UaiCmdTool(argparse.ArgumentParser())
        # sys.argv = ['any', 'translate']
        # for k in self.params.keys():
        #     if k=='public_key' or k== 'private_key' \
        #             or k == 'os' or k =='language' or k=='ai_arch_v' or k=='os_deps' or k=='pip':
        #         if self.params[k]:
        #             sys.argv.append('--' + k)
        #             sys.argv.append(self.params[k])
        # self.translateTool._load_args()
        self.translateTool = UaiCmdTool(self.parser)
        self.translateTool.conf_params = params
        self.translateTool.translate_pkg_params()

    def _get_baseimage(self):
        self.baseimageTool = UaiCmdTool(self.parser)

        #get gpu image
        self._translate_args(self.config.params)
        self.baseimageTool.conf_params['baseimage'] = self.baseimageTool.get_base_image(self.translateTool.conf_params)

        #get cpu image
        self.config.params["accelerator"] = "cpu"
        self._translate_args(self.config.params)
        self.baseimageTool.conf_params['cpuimage'] = self.baseimageTool.get_base_image(self.translateTool.conf_params)

    def _bulid_userimage(self):
        uai_logger.info("Docker login on " + DOCKER_REGISTRY)
        retcode = subprocess.check_call(["docker", "login", "-u", self.baseimageTool.conf_params["uhub_username"], "-p", self.baseimageTool.conf_params["uhub_password"], DOCKER_REGISTRY],
                                        stderr=subprocess.STDOUT)
        if retcode != 0: return

        '''
        Build cpu image for local training
        '''
        uai_logger.info("Pull base image from " + DOCKER_REGISTRY)
        retcode = subprocess.check_call(["docker", "pull", self.baseimageTool.conf_params["cpuimage"]],
                                        stderr=subprocess.STDOUT)
        if retcode != 0: return

        uai_logger.info("Create CPU Dockerfile")
        dockerbuf = []
        dockerbuf.append("From " + self.baseimageTool.conf_params["cpuimage"] + "\n")
        dockerbuf.append("ADD " + "./" + self.baseimageTool.conf_params["code_path"]  + " /data/\n")
        with open(TMP_CPU_DOCKER_FILE, 'w') as f:
            f.write(''.join(dockerbuf))

        uai_logger.info("Build CPU user image")
        userimage = self.baseimageTool.conf_params["uhub_imagename"] + "-cpu"
        if self.baseimageTool.conf_params["uhub_imagetag"]:
            userimage = userimage +  ":" + self.baseimageTool.conf_params["uhub_imagetag"] + "_" + DOCKER_TAG_SUFFIX
        else:
            userimage = userimage + ":" + DOCKER_TAG_SUFFIX
        retcode = subprocess.check_call(["docker", "build", "-t", userimage, "-f", TMP_CPU_DOCKER_FILE, "."],
                                        stderr=subprocess.STDOUT)
        self.usercpuimage = userimage

        '''
        Build actual image for training
        '''
        uai_logger.info("Build user image")
        uai_logger.info("Pull base image from " + DOCKER_REGISTRY)
        retcode = subprocess.check_call(["docker", "pull", self.baseimageTool.conf_params["baseimage"]],
                                        stderr=subprocess.STDOUT)
        if retcode != 0: return

        uai_logger.info("Create Dockerfile")
        dockerbuf = []
        dockerbuf.append("From " + self.baseimageTool.conf_params["baseimage"] + "\n")
        dockerbuf.append("ADD " + "./" + self.baseimageTool.conf_params["code_path"]  + " /data/\n")
        with open(TMP_DOCKER_FILE, 'w') as f:
            f.write(''.join(dockerbuf))

        uai_logger.info("Build user image")
        userimage = DOCKER_REGISTRY + "/" + self.baseimageTool.conf_params["uhub_registry"] + "/" + \
                    self.baseimageTool.conf_params["uhub_imagename"]
        if self.baseimageTool.conf_params["uhub_imagetag"]:
            userimage = userimage +  ":" + self.baseimageTool.conf_params["uhub_imagetag"] + "_" + DOCKER_TAG_SUFFIX
        else:
            userimage = userimage + ":" + DOCKER_TAG_SUFFIX
        retcode = subprocess.check_call(["docker", "build", "-t", userimage, "-f", TMP_DOCKER_FILE, "."],
                                        stderr=subprocess.STDOUT)
        if retcode != 0: return
        self.userimage = userimage


    def _push_userimage(self):
        uai_logger.info("Push user image")
        retcode = subprocess.check_call(["docker", "push", self.userimage],
                                        stderr=subprocess.STDOUT)
        if retcode != 0: return

    def _gen_run_cmd(self):
        uai_logger.info("Generate run cmd")

        pycmd = "/data/" + \
            self.baseimageTool.conf_params["mainfile_path"] + " " + \
            self.baseimageTool.conf_params["train_params"]
        cpudockercmd = "sudo docker run -it -v " + \
            self.baseimageTool.conf_params["test_data_path"] + ":" + "/data/data " + \
            "-v " + self.baseimageTool.conf_params["test_output_path"] + ":" + "/data/output " + \
            self.usercpuimage + " " + "/bin/bash -c " + \
            "\"cd /data && /usr/bin/python " + pycmd + " " + "--work_dir=/data --data_dir=/data/data --output_dir=/data/output --log_dir=/data/output/log\""
        f = open(DOCKER_RUN_CMD_FILE, "w")
        f.write("CMD Used for deploying: " + pycmd + "\n")
        f.write("CMD for CPU local test: " + cpudockercmd + "\n")
        print("CMD Used for deploying:")
        print(pycmd)
        print("CMD for CPU local test:")
        print(cpudockercmd)

        if self.accelerator == "gpu":
            gpudockercmd = "sudo nvidia-docker run -it -v " + \
                self.baseimageTool.conf_params["test_data_path"] + ":" + "/data/data " + \
                "-v " + self.baseimageTool.conf_params["test_output_path"] + ":" + "/data/output " + \
                self.userimage + " " + "/bin/bash -c " + \
                "\"cd /data && /usr/bin/python " + pycmd + " " + "--work_dir=/data --data_dir=/data/data --output_dir=/data/output --log_dir=/data/output/log\""
            f.write("CMD for GPU local test: " + gpudockercmd + "\n")
            print("CMD for GPU local test:")
            print(gpudockercmd)
        print("You can check these cmd later in file:" + DOCKER_RUN_CMD_FILE)
        f.close()

    def pack(self):
        self._load_args()
        self._get_baseimage()
        # self._bulid_userimage()
        # self._push_userimage()
        # self._gen_run_cmd()