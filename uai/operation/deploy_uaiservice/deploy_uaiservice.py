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

import time
from uai.utils.utils import val_to_str
from uai.utils.logger import uai_logger
from uai.utils.utils import parse_unrequired_args
from uai.operation.base_operation import BaseUaiServiceOp
from uai.api.deploy_uai_service import DeployUAIServiceApiOp
from uai.api.get_uai_available_env_pkg import GetUAIAvailableEnvPkgApiOp
from uai.api.check_uai_deploy_progress import CheckUAIDeployProgressApiOp

class UaiServiceDeployByUfileOp(BaseUaiServiceOp):
    """
    The Base Deploy Tool Class with UAI
    """
    def __init__(self, parser):
        super(UaiServiceDeployByUfileOp, self).__init__(parser)

    def _add_deploy_args(self, deploy_parser):
        deploy_parse = deploy_parser.add_argument_group(
            'Deploy-Params', 'Deploy Parameters, help to build user images for service')
        deploy_parse.add_argument(
            '--service_id',
            type=str,
            required=True,
            help='the service id of UAI Inference')
        deploy_parse.add_argument(
            '--os',
            type=str,
            default="ubuntu-14.04.05",
            help='the type of the docker os')
        deploy_parse.add_argument(
            '--language',
            type=str,
            default='python-2.7.6',
            help='the language of the docker')
        deploy_parse.add_argument(
            '--ai_arch_v',
            type=str,
            required=False,
            help='AI architecture and specific version')
        deploy_parse.add_argument(
            '--bimg_name',
            type=str,
            required=False,
            help='the base image of current service, containing tag')
        deploy_parse.add_argument(
            '--ufile_url',
            type=str,
            required=True,
            help='the url path given by ufile')
        deploy_parse.add_argument(
            '--os_deps',
            type=str,
            required=False,
            help='the dependency of the ubuntu apt-get')
        deploy_parse.add_argument(
            '--pip',
            type=str,
            required=False,
            help='the dependency of the python pip')

    def _add_args(self):
        super(UaiServiceDeployByUfileOp, self)._add_args()
        self._add_deploy_args(self.parser)


    def _parse_deploy_args(self, args):
        self.service_id = args['service_id']
        if 'bimg_name' in args and args['bimg_name'] != None:
            self.bimg_name = args['bimg_name']
            self.os_version = parse_unrequired_args('os', args)
            self.python_version = parse_unrequired_args('language', args)
            self.ai_arch_v = parse_unrequired_args('ai_arch_v', args)
        elif ('os' in args and args['os'] != None) and ('language' in args and args['language'] != None) and ('ai_arch_v' in args and args['ai_arch_v'] != None):
            self.os_version = args['os']
            self.python_version = args['language']
            self.ai_arch_v = args['ai_arch_v']
            self.bimg_name = parse_unrequired_args('bimg_name', args)
        else:
            raise ValueError('Parameters "os, language, ai_arch_v" and "bimg_name" should not be nil at same time.')


        self.ufile_url = args['ufile_url']
        self.os_deps = parse_unrequired_args('os_deps', args)
        self.pip = parse_unrequired_args('pip', args)

    def _parse_args(self, args):
        super(UaiServiceDeployByUfileOp, self)._parse_args(args)
        self._parse_deploy_args(args)

    def _translate_pkgs_to_ids(self, pkgtype, pkgs):
        if pkgs == '':
            return ''
        retlist = []
        pkgs = pkgs.split(',')
        env_op = GetUAIAvailableEnvPkgApiOp(
            self.public_key,
            self.private_key,
            pkgtype,
            self.project_id,
            self.region,
            self.zone
        )
        succ, result = env_op.call_api()
        if succ is False:
            raise RuntimeError("Error get {0} info from server".format(pkgtype))
        for avpkg in result['PkgSet']:
            for pkg in pkgs:
                if pkgtype == 'OS' or pkgtype == 'Python' or pkgtype == 'AIFrame':
                    versionsplit = pkg.rfind('-')
                    if versionsplit > 0:
                        if avpkg["PkgName"] == pkg[:versionsplit] and (
                                avpkg["PkgVersion"] == "" or avpkg["PkgVersion"] == pkg[versionsplit + 1:]):
                            pkgs.remove(pkg)
                            retlist.append(avpkg["PkgId"])
                    elif versionsplit < 0:
                        if avpkg["PkgName"] == pkg:
                            pkgs.remove(pkg)
                            retlist.append(avpkg["PkgId"])
                else:
                    if avpkg["PkgName"] == pkg:
                        pkgs.remove(pkg)
                        retlist.append(avpkg["PkgId"])
        if len(pkgs) != 0:
            raise RuntimeError("Some {0} package is not supported: {1}".format(pkgtype, pkgs))
        retlist = val_to_str(retlist)
        return retlist

    def cmd_run(self, args):
        self._parse_args(args)

        os_id = self._translate_pkgs_to_ids('OS', self.os_version)
        python_id = self._translate_pkgs_to_ids('Python', self.python_version)
        ai_arch_id = self._translate_pkgs_to_ids('AIFrame', self.ai_arch_v)
        apt_ids = self._translate_pkgs_to_ids('AptGet', self.os_deps)
        pip_ids = self._translate_pkgs_to_ids('Pip', self.pip)

        deployOp = DeployUAIServiceApiOp(
            public_key=self.public_key,
            private_key=self.private_key,
            project_id=self.project_id,
            region=self.region,
            zone=self.zone,
            service_id=self.service_id,
            os_version=os_id,
            python_version=python_id,
            bimg_name=self.bimg_name,
            ai_frame_version=ai_arch_id,
            ufile_url=self.ufile_url,
            apt_list=apt_ids,
            pip_list=pip_ids,
        )

        succ, rsp = deployOp.call_api()
        if not succ:
            raise RuntimeError('Call DeployUAIService fail, Error Message:{0}'.format(rsp['Message']))

        for i in range(0, 200):
            deploy_progress_Op = CheckUAIDeployProgressApiOp(
                public_key=self.public_key,
                private_key=self.private_key,
                project_id=self.project_id,
                region=self.region,
                zone=self.zone,
                service_id=self.service_id,
                uimg_name=rsp['UimgName']
            )
            deploy_process_succ, deploy_process_rsp = deploy_progress_Op.call_api()
            if deploy_process_succ == False \
                    or deploy_process_rsp['Status'] == 'Error' \
                    or deploy_process_rsp['Status'] == 'Started' \
                    or deploy_process_rsp['Status'] == 'ToStart':
                break
            time.sleep(10)

        return succ, rsp




















