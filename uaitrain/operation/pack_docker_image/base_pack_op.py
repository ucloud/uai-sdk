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
import json
import subprocess

from uai.utils.logger import uai_logger
from uaitrain.operation.base_op import BaseUAITrainOp
from uaitrain.api.get_env_pkg import GetUAITrainEnvPkgAPIOp
from uaitrain.api.check_and_get_base_image_op import CheckAndGetUAITrainBasesImageAPIOp

DOCKER_PUBLIC_REGISTRY = "uhub.ucloud.cn"
DOCKER_INTERNAL_REGISTRY = "uhub.service.ucloud.cn"
DOCKER_TAG_SUFFIX = "uaitrain"
TMP_CPU_DOCKER_FILE = "uaitrain-cpu.Dockerfile"
TMP_DOCKER_FILE = "uaitrain.Dockerfile"
DOCKER_RUN_CMD_FILE = "uaitrain_cmd.txt"


class BaseUAITrainDockerImagePackOp(BaseUAITrainOp):
    def __init__(self, parser):
        super(BaseUAITrainDockerImagePackOp, self).__init__(parser)
        self.dcoker_register = DOCKER_PUBLIC_REGISTRY

    def _add_pack_args(self, pack_parser):
        pack_parser.add_argument(
            '--os',
            type=str,
            default='ubuntu',
            help='The docker os version')
        pack_parser.add_argument(
            '--python_version',
            type=str,
            default='python-2.7.6',
            help='The docker python version')
        pack_parser.add_argument(
            '--ai_arch_v',
            type=str,
            help='The AI framework and its version, e.g., tensorflow-1.1.0')
        pack_parser.add_argument(
            '--acc_type',
            type=str,
            default='gpu',
            help='The accelerator id, e.g., GPU')

    def _add_image_args(self, pack_parser):
        uhub_parse = pack_parser.add_argument_group(
            'Docker-Params', 'Docker Parameters, help to upload docker image automatically')
        uhub_parse.add_argument(
            '--uhub_username',
            type=str,
            required=True,
            help='Username to login uhub, should be your account name')
        uhub_parse.add_argument(
            '--uhub_password',
            type=str,
            required=True,
            help='Password used to login uhub, should be your account password')
        uhub_parse.add_argument(
            '--uhub_registry',
            type=str,
            required=True,
            help='The name of registry owned by user on ucloud console')
        uhub_parse.add_argument(
            '--uhub_imagename',
            type=str,
            required=True,
            help='The docker image name')
        uhub_parse.add_argument(
            '--uhub_imagetag',
            type=str,
            default='uaitrain',
            help='The docker image tag')
        pack_parser.add_argument(
            '--internal_uhub',
            type=str,
            choices=['true', 'false'],
            default='false',
            help='Whether to use internal uhub. Use it when your are in UCloud Uhost')

    def _add_code_args(self, pack_parser):
        code_parse = pack_parser.add_argument_group(
            'Code-Params', 'Code Parameters, help to pack user code into docker image')
        code_parse.add_argument(
            '--code_path',
            type=str,
            required=True,
            help='The path of the user program containing all code files')
        code_parse.add_argument(
            '--mainfile_path',
            type=str,
            required=True,
            help='The related path of main python file considering code_path as root')
        code_parse.add_argument(
            '--train_params',
            type=str,
            default="",
            help='The params used in training')

        cmd_gen_parse = pack_parser.add_argument_group(
            'Cmd-Gen-Params', 'Cmd generate params')
        cmd_gen_parse.add_argument(
            '--test_data_path',
            type=str,
            required=True,
            help='The data dir for local test')
        cmd_gen_parse.add_argument(
            '--test_output_path',
            type=str,
            required=True,
            help='The output dir for local test')

    def _add_args(self):
        pack_parser = self.parser.add_parser('pack', help='Pack local docker image for uai train')
        self.pack_parser = pack_parser
        self._add_account_args(pack_parser)
        self._add_pack_args(pack_parser)
        self._add_image_args(pack_parser)
        self._add_code_args(pack_parser)

    def _parse_args(self, args):
        super(BaseUAITrainDockerImagePackOp, self)._parse_args(args)

        if ('ai_arch_v' in args) is False:
            print("AI Framework and its version is required, e.g. --ai_arch_v=tensorflow-1.1.0")
            return False

        self.os_v_name = args['os']
        self.python_v_name = args['python_version']
        self.ai_arch_v_name = args['ai_arch_v']
        self.acc_id_name = args['acc_type']

        self.uhub_username = args['uhub_username']
        self.uhub_password = args['uhub_password']
        self.uhub_registry = args['uhub_registry']
        self.uhub_imagename = args['uhub_imagename']
        self.uhub_imagetag = args['uhub_imagetag']
        self.internal_uhub = args['internal_uhub']

        self.internal_uhub = True if self.internal_uhub == 'true' else False

        if self.internal_uhub is True:
            self.dcoker_register = DOCKER_INTERNAL_REGISTRY

        self.code_path = args['code_path']
        self.mainfile_path = args['mainfile_path']
        self.train_params = args['train_params']
        self.test_data_path = args['test_data_path']
        self.test_output_path = args['test_output_path']

        return True

    def _translate_pkg_to_id(self, pkgtype, pkg):
        uai_logger.info("Start download {0} package info".format(pkgtype))

        api_op = GetUAITrainEnvPkgAPIOp(self.pub_key,
                                        self.pri_key,
                                        pkgtype,
                                        self.project_id,
                                        self.region,
                                        self.zone)
        succ, result = api_op.call_api()

        if succ is False:
            raise RuntimeError("Error get {0} info from server".format(pkgtype))

        for avpkg in result['PkgSet']:
            if pkgtype == 'OS' or pkgtype == 'Python' or pkgtype == 'AIFrame':
                versionsplit = pkg.rfind('-')
                if versionsplit > 0:
                    if avpkg["PkgName"] == pkg[:versionsplit] and (
                                    avpkg["PkgVersion"] == "" or avpkg["PkgVersion"] == pkg[versionsplit + 1:]):
                        return avpkg["PkgId"]
                elif versionsplit < 0:
                    if avpkg["PkgName"] == pkg:
                        return avpkg["PkgId"]
            else:
                if avpkg["PkgName"] == pkg:
                    return avpkg["PkgId"]

        uai_logger.error("Some {0} package is not supported: {1}".format(pkgtype, pkg))
        raise RuntimeError("Some {0} package is not supported: {1}".format(pkgtype, pkg))
        return None

    def _build_cpu_userimage(self):
        '''
        Build cpu image for local training
        '''
        uai_logger.info("Pull base image from " + self.dcoker_register)
        retcode = subprocess.check_call(["docker", "pull", self.cpu_image], stderr=subprocess.STDOUT)
        if retcode != 0:
            raise RuntimeError("Error pull image: {0}, Please check your network".format(self.cpu_image))

        uai_logger.info("Create CPU Dockerfile")
        dockerbuf = []
        dockerbuf.append("From " + self.cpu_image + "\n")
        dockerbuf.append("ADD " + "./" + self.code_path + " /data/\n")
        with open(TMP_CPU_DOCKER_FILE, 'w') as f:
            f.write(''.join(dockerbuf))

        uai_logger.info("Build CPU user image")
        userimage = self.uhub_imagename + "-cpu"
        if self.uhub_imagetag != None and self.uhub_imagetag != "":
            userimage = userimage + ":" + self.uhub_imagetag
        else:
            userimage = userimage + ":" + DOCKER_TAG_SUFFIX
        retcode = subprocess.check_call(["docker", "build", "-t", userimage, "-f", TMP_CPU_DOCKER_FILE, "."],
                                        stderr=subprocess.STDOUT)
        if retcode != 0:
            raise RuntimeError("Error build image: {0}, Please retry".format(userimage))

        self.user_cpu_image = userimage

    def _build_gpu_userimage(self):
        '''
        Build actual image for training
        '''
        uai_logger.info("Build training docker image")
        uai_logger.info("Pull base image from " + self.dcoker_register)
        retcode = subprocess.check_call(["docker", "pull", self.acc_image],
                                        stderr=subprocess.STDOUT)
        if retcode != 0:
            raise RuntimeError("Error pull image: {0}, Please check your network".format(self.acc_image))

        uai_logger.info("Create GPU Dockerfile")
        dockerbuf = []
        dockerbuf.append("From " + self.acc_image + "\n")
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

    def _push_gpu_userimage(self):
        uai_logger.info("Push user image")
        retcode = subprocess.check_call(["docker", "push", self.user_gpu_image],
                                        stderr=subprocess.STDOUT)
        if retcode != 0:
            raise RuntimeError("Error push image {0}, Please check your network".format(self.user_gpu_image))

    def _gen_pycmd(self):
        pycmd = "/data/" + self.mainfile_path + " " + self.train_params
        return pycmd

    def _gen_cpu_docker_cmd(self, pycmd):
        cpu_docker_cmd = "sudo docker run -it " + \
                         "-v " + self.test_data_path + ":" + "/data/data " + \
                         "-v " + self.test_output_path + ":" + "/data/output " + \
                         self.user_cpu_image + " " + "/bin/bash -c " + \
                         "\"cd /data && /usr/bin/python " + pycmd + " " + "--work_dir=/data --data_dir=/data/data --output_dir=/data/output --log_dir=/data/output\""
        return cpu_docker_cmd

    def _gen_gpu_docker_cmd(self, pycmd):
        gpu_docker_cmd = "sudo nvidia-docker run -it " + \
                         "-v " + self.test_data_path + ":" + "/data/data " + \
                         "-v " + self.test_output_path + ":" + "/data/output " + \
                         self.user_gpu_image + " " + "/bin/bash -c " + \
                         "\"cd /data && /usr/bin/python " + pycmd + " " + "--work_dir=/data --data_dir=/data/data --output_dir=/data/output --log_dir=/data/output\""
        return gpu_docker_cmd

    def _gen_run_cmd(self):
        f = open(DOCKER_RUN_CMD_FILE, "w")

        """ Python cmd used in deploy
        """
        pycmd = self._gen_pycmd()
        f.write("CMD Used for deploying: " + pycmd + "\n")
        print("CMD Used for deploying: {0}".format(pycmd))

        """ Cmd used in local CPU train test
        """
        cpu_docker_cmd = self._gen_cpu_docker_cmd(pycmd)
        f.write("CMD for CPU local test: " + cpu_docker_cmd + "\n")
        print("CMD for CPU local test: {0}".format(cpu_docker_cmd))

        if self.acc_id_name == 'gpu':
            """ Cmd used in local GPU train test
            """
            gpu_docker_cmd = self._gen_gpu_docker_cmd(pycmd)
            f.write("CMD for GPU local test: " + gpu_docker_cmd + "\n")
            print("CMD for GPU local test: {0}".format(gpu_docker_cmd))

        f.close()
        print("You can check these cmd later in file: {0}".format(DOCKER_RUN_CMD_FILE))

    def _build_userimage(self):
        uai_logger.info("Docker login on " + self.dcoker_register)
        retcode = subprocess.check_call(
            ["docker", "login", "-u", self.uhub_username, "-p", self.uhub_password, "-e", "x", self.dcoker_register],
            stderr=subprocess.STDOUT)
        if retcode != 0:
            raise RuntimeError("Error login to uhub, Please check your username and password, or try with sudo")

        self._build_cpu_userimage()

        if self.acc_id_name == 'gpu':
            self._build_gpu_userimage()
            self._push_gpu_userimage()

        self._gen_run_cmd()

    def check_interHub(self, baseimage):
        if baseimage.startswith(DOCKER_PUBLIC_REGISTRY) and self.internal_uhub is True:
            baseimage = baseimage.replace(DOCKER_PUBLIC_REGISTRY, DOCKER_INTERNAL_REGISTRY, 1)
        if baseimage.startswith(DOCKER_INTERNAL_REGISTRY) and self.internal_uhub is False:
            baseimage = baseimage.replace(DOCKER_INTERNAL_REGISTRY, DOCKER_PUBLIC_REGISTRY, 1)
        return baseimage

    def cmd_run(self, args):
        if self._parse_args(args) == False:
            return False

        os_v = self._translate_pkg_to_id('OS', self.os_v_name)
        python_v = self._translate_pkg_to_id('Python', self.python_v_name)
        ai_arch_v = self._translate_pkg_to_id('AIFrame', self.ai_arch_v_name)
        acc_id = self._translate_pkg_to_id('Accelerator', self.acc_id_name)

        get_acc_image_op = CheckAndGetUAITrainBasesImageAPIOp(
            self.pub_key,
            self.pri_key,
            os_v,
            python_v,
            ai_arch_v,
            acc_id,
            self.project_id,
            self.region,
            self.zone)

        succ, result = get_acc_image_op.call_api()
        acc_image_name = result['BimgName'][0]
        acc_image_name = self.check_interHub(acc_image_name)

        cpu_acc_id = self._translate_pkg_to_id('Accelerator', 'cpu')
        get_cpu_image_op = CheckAndGetUAITrainBasesImageAPIOp(
            self.pub_key,
            self.pri_key,
            os_v,
            python_v,
            ai_arch_v,
            cpu_acc_id,
            self.project_id,
            self.region,
            self.zone)
        succ, result = get_cpu_image_op.call_api()
        cpu_image_name = result['BimgName'][0]
        cpu_image_name = self.check_interHub(cpu_image_name)

        print(acc_image_name)
        print(cpu_image_name)

        self.acc_image = acc_image_name
        self.cpu_image = cpu_image_name

        self._build_userimage()
        