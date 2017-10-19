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
import tarfile
import subprocess
from datetime import datetime
from uai.utils.logger import uai_logger
from uai.operation.checkbase import UaiServiceCheckBaseImgExistOp

DOCKER_PUBLIC_REGISTRY = "uhub.ucloud.cn"
DOCKER_INTERNAL_REGISTRY = "uhub.service.ucloud.cn"
DOCKER_TAG_SUFFIX = "uaiservice"
TMP_DOCKER_FILE = "uaiservice.Dockerfile"
DOCKER_RUN_CMD_FILE = "uaiservice_cmd.txt"

class UaiServicePackOp(UaiServiceCheckBaseImgExistOp):
    """ The Base Pack Tool Class with UAI
    """
    def __init__(self, parser):
        super(UaiServicePackOp, self).__init__(parser)

        self.conf_params = {}
        self.filelist = []

    def _add_args(self, parser):
        super(UaiServicePackOp, self)._add_args(parser)
        uhub_parse = parser.add_argument_group(
            'Docker-Params', 'Docker Parameters, help to upload docker image automatically')
        uhub_parse.add_argument(
            '--uhub_username',
            type=str,
            required=True,
            help='username to login uhub, which is also username to ucloud console')
        uhub_parse.add_argument(
            '--uhub_password',
            type=str,
            required=True,
            help='password to login uhub, which is also password to ucloud console')
        uhub_parse.add_argument(
            '--uhub_registry',
            type=str,
            required=True,
            help='the name of registry owned by user on ucloud console')
        uhub_parse.add_argument(
            '--uhub_imagename',
            type=str,
            required=True,
            help='the name of user docker image, include image tag')
        uhub_parse.add_argument(
            '--in_uhost',
            type=str,
            choices=['yes', 'no'],
            default='no',
            help='Use it when your are in UCloud Uhost.')
        #add other params in subclasses#

    def _parse_args(self):
        super(UaiServicePackOp, self)._parse_args()
        if "ai_arch_v" in self.params:
            if self.platform != self.params["ai_arch_v"].lower().split('-')[0]:
                raise RuntimeError("ai_arch_v should be one version of " + self.platform)

        self.uhub_username = self.params['uhub_username']
        self.uhub_password = self.params['uhub_password']
        self.uhub_registry = self.params['uhub_registry']
        self.uhub_imagename = self.params['uhub_imagename']
        self.uhub_imagetag = self.uhub_imagename[self.uhub_imagename.rfind(':')+1:]

        print('tag:{0}'.format(self.uhub_imagetag))

        self.internal_uhub = True if self.params['in_uhost'] == 'yes' else False

        self.docker_register = DOCKER_PUBLIC_REGISTRY
        if self.internal_uhub is True:
            self.docker_register = DOCKER_INTERNAL_REGISTRY

    def _bulid_userimage(self):
        uai_logger.info("Docker login on " + self.docker_register)
        retcode = subprocess.check_call(["docker", "login", "-u", self.uhub_username, "-p",
                                         self.uhub_password, self.docker_register],
                                        stderr=subprocess.STDOUT)
        if retcode != 0:
            raise RuntimeError("Error login to uhub, Please check your username and password, or try with sudo")
        # uai_logger.info("Pull base image from " + self.docker_register)
        # retcode = subprocess.check_call(["docker", "pull", self.baseimage], stderr=subprocess.STDOUT)
        # if retcode != 0:
        #     raise RuntimeError("Error pull image: {0}, Please check your network".format(self.baseimage))

        uai_logger.info("Create Dockerfile")
        dockerbuf = []
        dockerbuf.append("From " + self.baseimage + "\n")
        if self.platform == 'caffe':
            dockerbuf.append("ENV PYTHONPATH /root/caffe/python\n")

        dockerbuf.append("EXPOSE 8080\n")
        dockerbuf.append("ADD " + "./" + self.tar_name + " /ai-ucloud-client-django/\n")
        dockerbuf.append("ENV UAI_SERVICE_CONFIG /ai-ucloud-client-django/ufile.json\n")
        dockerbuf.append("CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi" + "\n")

        with open(TMP_DOCKER_FILE, 'w') as f:
            f.write(''.join(dockerbuf))
        '''
        Build user image
        '''
        uai_logger.info("Build user image")
        userimage = self.docker_register + "/" + self.uhub_registry + "/" + self.uhub_imagename
        if self.uhub_imagetag == '':
        #     userimage = userimage + ":" + self.uhub_imagetag
        # else:
            userimage = userimage + ":" + DOCKER_TAG_SUFFIX
        retcode = subprocess.check_call(["docker", "build", "-t", userimage, "-f", TMP_DOCKER_FILE, "."],
                                        stderr=subprocess.STDOUT)
        if retcode != 0:
            raise RuntimeError("Error build image: {0}, Please retry".format(userimage))
        self.userimage = userimage

    def _push_userimage(self):
        uai_logger.info("Push user image")
        retcode = subprocess.check_call(["docker", "push", self.userimage],
                                        stderr=subprocess.STDOUT)
        if retcode != 0:
            raise RuntimeError("Error push image {0}, Please check your network".format(self.userimage))

    def _pack(self):
        self._bulid_userimage()
        self._push_userimage()
        print('upload docker images successful. images:{0}'.format(self.userimage))

    def cmd_run(self, params):
        # get base image name
        succ, rsp = super(UaiServicePackOp, self).cmd_run(params)
        if len(rsp['BimgName']) != 0:
            self.baseimage = rsp['BimgName'][0]
            if self.baseimage.startswith(DOCKER_PUBLIC_REGISTRY) and self.internal_uhub is True:
                self.baseimage = self.baseimage.replace(DOCKER_PUBLIC_REGISTRY, DOCKER_INTERNAL_REGISTRY, 1)
            if self.baseimage.startswith(DOCKER_INTERNAL_REGISTRY) and self.internal_uhub is False:
                self.baseimage = self.baseimage.replace(DOCKER_INTERNAL_REGISTRY, DOCKER_PUBLIC_REGISTRY, 1)

        self._pack()