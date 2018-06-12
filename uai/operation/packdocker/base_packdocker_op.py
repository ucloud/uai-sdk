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
import json
import subprocess
from uai.operation.base_operation import BaseUaiServiceOp
from uai.utils.retcode_checker import *
from uai.api.check_uai_base_img_exist import CheckUAIBaseImgExistApiOp
from uai.api.get_uai_available_env_pkg import GetUAIAvailableEnvPkgApiOp

DOCKER_PUBLIC_REGISTRY = "uhub.ucloud.cn"
DOCKER_INTERNAL_REGISTRY = "uhub.service.ucloud.cn"
TMP_DOCKER_FILE = "uai_inference.Dockerfile"
DOCKER_RUN_CMD_FILE = "uai_inference_cmd.txt"

class UaiServiceDockerPackOp(BaseUaiServiceOp):
    """ The Base Docker Pack Tool Class with UAI
    """
    def __init__(self, parser):
        super(UaiServiceDockerPackOp, self).__init__(parser)
        self.conf_params = {}
        self.platform = ''

    def _add_env_args(self, packdocker_parser):
        env_parser = packdocker_parser.add_argument_group(
            'Env-Params', 'Env Parameters, help to choose docker env'
        )
        env_parser.add_argument(
            '--os',
            type=str,
            default='ubuntu',
            help='The docker os version')
        env_parser.add_argument(
            '--python_version',
            type=str,
            default='python-2.7.6',
            help='The docker python version')
        env_parser.add_argument(
            '--ai_arch_v',
            type=str,
            required=True,
            help='The AI framework and its version, e.g. tensorflow-1.1.0')

    def _add_uhub_args(self, pack_parser):
        uhub_parse = pack_parser.add_argument_group(
            'Uhub-Params', 'Uhub Parameters, help to upload docker image automatically'
        )
        uhub_parse.add_argument(
            '--uhub_username',
            type=str,
            required=True,
            help='Username to login uhub, should be your account name'
        )
        uhub_parse.add_argument(
            '--uhub_password',
            type=str,
            required=True,
            help='Password used to login uhub, should be your account password'
        )
        uhub_parse.add_argument(
            '--uhub_registry',
            type=str,
            required=True,
            help='The name of registry owned by user on ucloud console'
        )
        uhub_parse.add_argument(
            '--uhub_imagename',
            type=str,
            required=True,
            help='The name of generated image, containing imagetag'
        )
        uhub_parse.add_argument(
            '--in_host',
            type=str,
            choices=['yes', 'no'],
            default='no',
            help='Whether to use internal uhub. Use it when your are in UCloud Uhost'
        )

    def _add_conf_args(self, conf_parser):
        conf_parse = conf_parser.add_argument_group(
            'Conf-Params', 'Config Parameters, help to generate config files'
        )
        conf_parse.add_argument(
            '--pack_file_path',
            type=str,
            required=True,
            help='the relative directry of files'
        )
        conf_parse.add_argument(
            '--main_module',
            type=str,
            required=True,
            help='the main module of the user program'
        )
        conf_parse.add_argument(
            '--main_class',
            type=str,
            required=True,
            help='the main class name of the user program'
        )
        conf_parse.add_argument(
            '--model_dir',
            type=str,
            required=True,
            help='the directroy of models, relative to the pack_file_path'
        )

    def _add_args(self):
        self._add_account_args(self.parser)
        self._add_env_args(self.parser)
        self._add_uhub_args(self.parser)
        self._add_conf_args(self.parser)

    def _parse_env_args(self, args):
        self.os_version = args['os']
        self.python_version = args['python_version']
        self.ai_arch_v = args['ai_arch_v']

    def _parse_uhub_args(self, args):
        self.uhub_username = args['uhub_username']
        self.uhub_password = args['uhub_password']
        self.uhub_registry = args['uhub_registry']
        self.uhub_imagename = args['uhub_imagename']
        self.internal_uhub = True if args['in_host'] == 'yes' else False
        self.docker_register = DOCKER_PUBLIC_REGISTRY
        if self.internal_uhub is True:
            self.docker_register = DOCKER_INTERNAL_REGISTRY

    def _parse_conf_args(self, args):
        self.pack_file_path = args['pack_file_path']
        self.main_file = args['main_module']
        self.main_class =args['main_class']
        self.model_dir = args['model_dir']


    def _parse_args(self, args):
        self._parse_account_args(args)
        self._parse_env_args(args)
        self._parse_uhub_args(args)
        self._parse_conf_args(args)
        return True


    def _bulid_userimage(self):
        uai_logger.info("Docker login on " + self.docker_register)
        retcode = subprocess.check_call(["docker", "login", "-u", self.uhub_username, "-p",
                                         self.uhub_password, self.docker_register],
                                        stderr=subprocess.STDOUT)
        uai_logger.info("log in uhub retcode: " + str(retcode))
        if retcode != 0:
            raise RuntimeError("Error login to uhub, Please check your username and password, or try with sudo")

        uai_logger.info("Create Dockerfile")
        dockerbuf = []
        dockerbuf.append("From " + self.baseimage + "\n")
        if self.platform == 'caffe':
            dockerbuf.append("ENV PYTHONPATH /root/caffe/python\n")

        dockerbuf.append("EXPOSE 8080\n")
        dockerbuf.append("ADD " + "./" + self.pack_file_path + " /ai-ucloud-client-django/\n")
        if hasattr(self, 'conf_file') is True:
            conf_file = os.path.basename(self.conf_file)
            dockerbuf.append("ADD " + self.conf_file + " /ai-ucloud-client-django/" + conf_file + "\n")
        else:
            conf_file = 'ufile.json'
        dockerbuf.append("ENV UAI_SERVICE_CONFIG /ai-ucloud-client-django/" + conf_file + "\n")
        dockerbuf.append("CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi" + "\n")

        with open(TMP_DOCKER_FILE, 'w') as f:
            f.write(''.join(dockerbuf))

        uai_logger.info("Build user image")
        userimage = self.docker_register + "/" + self.uhub_registry + "/" + self.uhub_imagename
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

    def check_interHub(self, baseimage):
        if baseimage.startswith(DOCKER_PUBLIC_REGISTRY) and self.internal_uhub is True:
            baseimage = baseimage.replace(DOCKER_PUBLIC_REGISTRY, DOCKER_INTERNAL_REGISTRY, 1)
        if baseimage.startswith(DOCKER_INTERNAL_REGISTRY) and self.internal_uhub is False:
            baseimage = baseimage.replace(DOCKER_INTERNAL_REGISTRY, DOCKER_PUBLIC_REGISTRY, 1)
        return baseimage

    def _translate_pkg_to_id(self, pkgtype, pkg):
        uai_logger.info("Start download {0} package info".format(pkgtype))
        api_op = GetUAIAvailableEnvPkgApiOp(
            self.public_key,
            self.private_key,
            pkgtype,
            self.project_id,
            self.region,
            self.zone
        )
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
        raise RuntimeError("Some {0} package is not supported: {1}".format(pkgtype, pkg))

    def _check_baseimage_exist(self):
        os_id = self._translate_pkg_to_id('OS', self.os_version)
        python_id = self._translate_pkg_to_id('Python', self.python_version)
        ai_arch_id = self._translate_pkg_to_id('AIFrame', self.ai_arch_v)

        get_image_op = CheckUAIBaseImgExistApiOp(
            self.public_key,
            self.private_key,
            os_id,
            python_id,
            ai_arch_id,
            self.project_id,
            self.region,
            self.zone
        )

        succ, result = get_image_op.call_api()
        if succ != True:
            raise RuntimeError("Call CheckUAIBaseImageExist error, Error message: {}".format(result["Message"]))
        if len(result['BimgName']) == 0:
            raise RuntimeError("No image mactches current requests, please check your selection")
        baseimage = result['BimgName'][0]
        self.baseimage = self.check_interHub(baseimage)
        return True

    def _gen_jsonfile(self):
        with open(os.path.join(os.getcwd(), self.pack_file_path, 'ufile.json'), 'w') as f:
             json.dump(self.conf_params, f)

    def _packdocker(self):
        self._gen_jsonfile()
        self._check_baseimage_exist()
        self._bulid_userimage()
        self._push_userimage()
        uai_logger.info('upload docker images successful. images:{0}'.format(self.userimage))

    def cmd_run(self, args):
        if self._parse_args(args) == False:
            return False
        self._packdocker()