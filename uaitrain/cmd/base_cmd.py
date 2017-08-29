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
import time
import requests
from uai.utils.utils import _verfy_ac
from uai.utils.logger import uai_logger
from uaitrain.arch_conf.base_conf import *
from uai.utils.retcode_checker import *

MAX_POLL_STEPS = 200
DEPLOY_ID_FILE = './deploy_id.log'
UCLOUD_API_URL = 'http://api.ucloud.cn'
PARAMS_DEFAULT_REGION = 'cn-bj2'
PARAMS_DEFAULT_ZONE ='cn-bj2-04'
#UCLOUD_API_URL = 'http://api.pre.ucloudadmin.com'
#PARAMS_DEFAULT_REGION = "pre"
# UCLOUD_API_URL = 'http://127.0.0.1:8088'
# PARAMS_DEFAULT_REGION = "pre"
PARAMS_DEFAULT_BUSINESSGROUP = "Default"
PACKAGE_TYPE = {'os':'OS', 'language':'Python', 'ai_arch_v':'AIFrame', 'accelerator':'Accelerator'}

class UaiCmdTool(object):
    """ The Base Create Tool Class with UAI
    """
    def __init__(self, parser):
        self.parser = parser
        self.conf_params = {}
        self.cmd_params = {}
        self._add_args()

    def _add_args(self):
        self.config = ArchJsonConf('', self.parser)

    def cmd(self):
        """ Create the task of specified task id
        """
        # if self.conf_params:
        self._load_args()
        self._format_request_param()
        self._cmd_request()

    def _load_args(self):
        self.config.load_params()
        self.conf_params = self.config.params

    def _format_request_param(self):
        self._format_account_param()
        if self.conf_params['commands'] == 'checkbase':
            self._format_checkbase_param()
            self.cmd_url = UCLOUD_API_URL
        else:
            uai_logger.error("Command is not valid: {0} ".format(self.conf_params['commands']))
            raise RuntimeError("Command is not valid: {0} ".format(self.conf_params['commands']))

    def _format_account_param(self):
        self.cmd_params['PublicKey'] = self.conf_params['public_key']
        if self.conf_params['project_id']:
            self.cmd_params['ProjectId'] = self.conf_params['project_id']

    def _format_create_param(self):
        self.cmd_params['Region'] = PARAMS_DEFAULT_REGION
        self.cmd_params['Zone'] = PARAMS_DEFAULT_ZONE
        self.cmd_params['TrainJobName'] = self.conf_params['job_name']
        self.cmd_params['TrainPublicKey'] = self.conf_params['public_key']
        self.cmd_params['TrainPrivateKey'] = self.conf_params['private_key']
        self.cmd_params['TrainWorkId'] = self.conf_params['worker_id']
        self.cmd_params['CodeUhubPath'] = self.conf_params['uhub_path']
        self.cmd_params['DataUfilePath'] = self.conf_params['ufile_datapath']
        self.cmd_params['OutputUfilePath'] = self.conf_params['ufile_outputpath']
        self.cmd_params['DockerCmd'] = self.conf_params['docker_cmd']
        self.cmd_params['MaxExecuteTime'] = self.conf_params['max_exectime']
        self.cmd_params['Action'] = 'CreateUAITrainJob'

    def _format_checkbase_param(self):
        self.cmd_params['OSVersion'] = self.conf_params['os']
        self.cmd_params['PythonVersion'] = self.conf_params['language']
        self.cmd_params['AIFrameVersion'] = self.conf_params['ai_arch_v']
        self.cmd_params['AcceleratorID'] = self.conf_params['accelerator']
        # #Action must be applied at last
        self.cmd_params['Action'] = 'CheckUAITrainBaseImgExists'

    def _format_availableenv_param(self, type):
        self.cmd_params['PkgType'] = PACKAGE_TYPE[type]
        # #Action must be applied at last
        self.cmd_params['Action'] = 'GetUAITrainEnvPkg'

    def _cmd_request(self):
        if self.conf_params['commands'] == 'availableenv':
            self._cmd_writefile_package(self.conf_params['pkg_type'])
        else:
             self._cmd_common_request()

    def _cmd_common_request(self):
        if self.cmd_params.has_key('Signature'):
            self.cmd_params.pop('Signature')
        self.cmd_params['Signature'] = _verfy_ac(self.conf_params['private_key'],
                                                     self.cmd_params)
        uai_logger.info("Call http request: {0} ".format(get_request(self.cmd_url, params=self.cmd_params)))
        r = requests.get(self.cmd_url, params=self.cmd_params)
        self.rsp = json.loads(r.text, 'utf-8')
        if self.rsp["RetCode"] != 0:
            uai_logger.error("{0} Fail: [{1}]{2}".format(self.cmd_params["Action"], self.rsp["RetCode"], self.rsp["Message"].encode('utf-8')))
            raise RuntimeError("{0} Fail: [{1}]{2}".format(self.cmd_params["Action"], self.rsp["RetCode"], self.rsp["Message"].encode('utf-8')))
        else:
            del self.rsp['Action']
            uai_logger.info("{0} Success: {1}".format(self.cmd_params["Action"], get_response(self.rsp,0)))


    def _cmd_writefile_package(self, filepath):
        if self.cmd_params.has_key('Signature'):
            self.cmd_params.pop('Signature')
        self.cmd_params['Signature'] = _verfy_ac(self.conf_params['private_key'],
                                                     self.cmd_params)
        uai_logger.info("Call http request: {0} ".format(get_request(self.cmd_url, params=self.cmd_params)))
        r = requests.get(self.cmd_url, params=self.cmd_params)
        rsp = json.loads(r.text, 'utf-8')
        if rsp["RetCode"] != 0:
            uai_logger.error("{0} Fail: [{1}]{2}".format(self.cmd_params["Action"], rsp["RetCode"], rsp["Message"].encode('utf-8')))
            raise RuntimeError(
                "{0} Fail: [{1}]{2}".format(self.cmd_params["Action"], rsp["RetCode"], rsp["Message"].encode('utf-8')))
        else:
            with open(filepath, 'w') as f:
                json.dump(rsp["PkgSet"], f)


    def translate_pkg_params(self):
        if self.conf_params['os'] and type(self.conf_params['os']) is str:
            self.conf_params['os'] = \
                self._translate_pkg_to_id('os', self.conf_params['os'].split(','))[0]
        if self.conf_params['language'] and type(self.conf_params['language']) is str:
            self.conf_params['language'] = \
                self._translate_pkg_to_id('language', self.conf_params['language'].split(','))[0]
        if self.conf_params['ai_arch_v'] and type(self.conf_params['ai_arch_v']) is str:
            self.conf_params['ai_arch_v'] = \
                self._translate_pkg_to_id('ai_arch_v', self.conf_params['ai_arch_v'].split(','))[0]
        if self.conf_params['accelerator'] and type(self.conf_params['accelerator']) is str:
            self.conf_params['accelerator'] = \
                self._translate_pkg_to_id('accelerator', self.conf_params['accelerator'].split(','))[0]

    def _translate_pkg_to_id(self, pkgtype, pkglist):
        if not os.path.exists(pkgtype):
            # raise RuntimeError("{0} file doesn't found, please download from github "
            #                    "and put it under the same directory as deploy tool".format(pkgtype))
            uai_logger.info("Start download {0} package info".format(pkgtype))
            self.conf_params['pkg_type'] = pkgtype
            self._format_account_param()
            self._format_availableenv_param(pkgtype)
            self.cmd_url = UCLOUD_API_URL
            self._cmd_writefile_package(pkgtype)

        resultlist = []
        uai_logger.info("Start translate {0} package to their id, packages: {1}".format(pkgtype, pkglist))
        for avpkg in json.load(open(pkgtype), 'utf-8'):
            for pkg in pkglist:
                if pkgtype == 'os' or pkgtype == 'language' or pkgtype == 'ai_arch_v':
                    versionsplit = pkg.rfind('-')
                    if versionsplit >= 0:
                        if avpkg["PkgName"] == pkg[:versionsplit] and (
                                avpkg["PkgVersion"] == "" or avpkg["PkgVersion"] == pkg[versionsplit + 1:]):
                            pkglist.remove(pkg)
                            resultlist.append(avpkg["PkgId"])
                    elif versionsplit < 0:
                        if avpkg["PkgName"] == pkg:
                            pkglist.remove(pkg)
                            resultlist.append(avpkg["PkgId"])
                else:
                    if avpkg["PkgName"] == pkg:
                        pkglist.remove(pkg)
                        resultlist.append(avpkg["PkgId"])

        if len(pkglist) <> 0:
            uai_logger.error("Some {0} package is not supported: {1}".format(pkgtype, pkglist))
            raise RuntimeError("Some {0} package is not supported: {1}".format(pkgtype, pkglist))

        uai_logger.info("End translate {0} package to their id, result: {1}".format(pkgtype, resultlist))
        return resultlist

    def get_base_image(self, conf_params):
        self.conf_params = conf_params
        self.conf_params["commands"] = "checkbase"
        self._format_account_param()
        self._format_checkbase_param()
        self.cmd_url = UCLOUD_API_URL
        self._cmd_common_request()
        return self.rsp["BimgName"][0]