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
from uai.arch_conf.base_conf import *
from uai.utils.retcode_checker import *

MAX_POLL_STEPS = 200
DEPLOY_ID_FILE = './deploy_id.log'
UCLOUD_API_URL = 'http://api.ucloud.cn'
PARAMS_DEFAULT_REGION = "cn-bj2"
#UCLOUD_API_URL = 'http://api.pre.ucloudadmin.com'
#PARAMS_DEFAULT_REGION = "pre"
#UCLOUD_API_URL = 'http://127.0.0.1:8088'
#PARAMS_DEFAULT_REGION = "pre"
PARAMS_DEFAULT_BUSINESSGROUP = "Default"
PACKAGE_TYPE = {'os':'OS', 'language':'Python', 'ai_arch':'AIFrame', 'os_deps':'AptGet', 'pip':'Pip'}

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

    def _load_args(self):
        self.config.load_params()
        self.conf_params = self.config.params

    def _format_request_param(self):
        self._format_account_param()
        if self.conf_params['commands'] == 'create':
            self._format_create_param()
            self.cmd_url = UCLOUD_API_URL
        elif self.conf_params['commands'] == 'listservice':
            self._format_listservice_param()
            self.cmd_url = UCLOUD_API_URL
            print(self.cmd_params)
        elif self.conf_params['commands'] == 'listversion':
            self._format_listversion_param()
            self.cmd_url = UCLOUD_API_URL
        elif self.conf_params['commands'] == 'delete':
            self._format_delete_param()
            self.cmd_url = UCLOUD_API_URL
        elif self.conf_params['commands'] == 'stop':
            self._format_stop_param()
            self.cmd_url = UCLOUD_API_URL
        elif self.conf_params['commands'] == 'start':
            self._format_start_param()
            self.cmd_url = UCLOUD_API_URL
        elif self.conf_params['commands'] == 'modifyname':
            self._format_modifyname_param()
            self.cmd_url = UCLOUD_API_URL
        elif self.conf_params['commands'] == 'modifyweight':
            self._format_modifyweight_param()
            self.cmd_url = UCLOUD_API_URL
        elif self.conf_params['commands'] == 'availableenv':
            self._format_availableenv_param()
            self.cmd_url = UCLOUD_API_URL
        elif self.conf_params['commands'] == 'checkbase':          
            self._format_checkbase_param()
            self.cmd_url = UCLOUD_API_URL
        # elif self.conf_params['commands'] == 'translate':
        #     self._format_translate_param()
        elif self.conf_params['commands'] == 'deploy':
            self._format_deploy_param()
            self.cmd_url = UCLOUD_API_URL
        elif self.conf_params['commands'] == 'checkprogress':
            self._format_checkprogress_param()
            self.cmd_url = UCLOUD_API_URL
        else:
            uai_logger.error("Command is not valid: {0} ".format(self.conf_params['commands']))
            raise RuntimeError("Command is not valid: {0} ".format(self.conf_params['commands']))

    def _format_account_param(self):
        self.cmd_params['PublicKey'] = self.conf_params['public_key']
        if self.conf_params['project_id']:
            self.cmd_params['ProjectId'] = self.conf_params['project_id']

    def _format_create_param(self):
        self.cmd_params['Action'] = 'CreateUAIService'
        self.cmd_params['Region'] = PARAMS_DEFAULT_REGION
        self.cmd_params['SrvName'] = self.conf_params['service_name']
        if PARAMS_DEFAULT_REGION == 'pre':
            self.cmd_params['CPU'] = 1
            self.cmd_params['Memory'] = 1
        else:
            self.cmd_params['CPU'] = self.conf_params['cpu']
            self.cmd_params['Memory'] = self.conf_params['memory']
        self.cmd_params['BusinessGroup'] = PARAMS_DEFAULT_BUSINESSGROUP

    def _format_listservice_param(self):
        self.cmd_params['Action'] = 'GetUAIServiceList'
        self.cmd_params['Region'] = PARAMS_DEFAULT_REGION
        self.cmd_params['ServiceID'] = self.conf_params['service_id'] if self.conf_params['service_id'] else ''
        self.cmd_params['Offset'] = ''
        self.cmd_params['Limit'] = ''

    def _format_listversion_param(self):
        self.cmd_params['Action'] = 'GetUAISrvVersionList'
        self.cmd_params['Region'] = PARAMS_DEFAULT_REGION
        self.cmd_params['ServiceID'] = self.conf_params['service_id']
        self.cmd_params['SrvVersion'] = self.conf_params['service_version'] if self.conf_params['service_version'] else ''
        self.cmd_params['Offset'] = ''
        self.cmd_params['Limit'] = ''

    def _format_delete_param(self):
        self.cmd_params['Action'] = 'DeleteUAIService'
        self.cmd_params['Region'] = PARAMS_DEFAULT_REGION
        self.cmd_params['ServiceID'] = self.conf_params['service_id']
        self.cmd_params['SrvPaasID'] = self.conf_params['paas_id'] if self.conf_params['paas_id'] else ''
        self.cmd_params['SrvVersion'] = self.conf_params['service_version'] if self.conf_params['service_version'] else ''

    def _format_stop_param(self):
        self.cmd_params['Action'] = 'StopUAIService'
        self.cmd_params['Region'] = PARAMS_DEFAULT_REGION
        self.cmd_params['ServiceID'] = self.conf_params['service_id']
        self.cmd_params['SrvPaasID'] = self.conf_params['paas_id']
        self.cmd_params['SrvVersion'] = self.conf_params['service_version'] if self.conf_params['service_version'] else ''

    def _format_start_param(self):
        self.cmd_params['Action'] = 'StartUAIService'
        self.cmd_params['Region'] = PARAMS_DEFAULT_REGION
        self.cmd_params['ServiceID'] = self.conf_params['service_id']
        self.cmd_params['SrvPaasID'] = self.conf_params['paas_id']
        self.cmd_params['SrvVersion'] = self.conf_params['service_version']

    def _format_modifyname_param(self):
        self.cmd_params['Action'] = 'ModifyUAISrvName'
        self.cmd_params['Region'] = PARAMS_DEFAULT_REGION
        self.cmd_params['ServiceID'] = self.conf_params['service_id']
        self.cmd_params['SrvName'] = self.conf_params['service_name']

    def _format_modifyweight_param(self):
        self.cmd_params['Action'] = 'ModifyUAISrvVersionWeight'
        self.cmd_params['Region'] = PARAMS_DEFAULT_REGION
        self.cmd_params['ServiceID'] = self.conf_params['service_id']
        self.cmd_params['SrvVersion'] = self.conf_params['service_version']
        self.cmd_params['SrvPaasID'] = self.conf_params['paas_id']
        self.cmd_params['DeployWeight'] = self.conf_params['deploy_weight']

    def _format_availableenv_param(self):
        self.cmd_params['Action'] = 'GetUAIAvailableEnvPkg'
        self.cmd_params['PkgType'] = PACKAGE_TYPE[self.conf_params['pkg_type']]


    def _format_checkbase_param(self):
        self.translate_pkg_params()
        self.cmd_params['OSVersion'] = self.conf_params['os']
        self.cmd_params['PythonVersion'] = self.conf_params['language']
        self.cmd_params['AIFrameVersion'] = self.conf_params['ai_arch_v']
        # #Action must be applied at last
        self.cmd_params['Action'] = 'CheckUAIBaseImgExist'


    # def _format_translate_param(self):
    #     # run checkbase to ensure os, language, ai_arch is valid
    #     self.conf_params['commands'] = 'checkbase'
    #     self._format_checkbase_param()
    #     self.cmd_url = UCLOUD_API_URL
    #     self._cmd_request()
    #
    #     # translate apt-get, pip to package id
    #     if self.conf_params['os_deps']:
    #         self.conf_params['os_deps'] = self._translate_pkg_to_id('aptget', self.conf_params['os_deps'].split(','))
    #     if self.conf_params['pip']:
    #         self.conf_params['pip'] = self._translate_pkg_to_id('pip', self.conf_params['pip'].split(','))

    def translate_pkg_params(self):
        if self.conf_params['os']:
            self.conf_params['os'] = \
                self._translate_pkg_to_id('os', self.conf_params['os'].split(','))[0]
        if self.conf_params['language']:
            self.conf_params['language'] = \
                self._translate_pkg_to_id('language', self.conf_params['language'].split(','))[0]
        if self.conf_params['ai_arch_v']:
            self.conf_params['ai_arch_v'] = \
                self._translate_pkg_to_id('ai_arch', self.conf_params['ai_arch_v'].split(','))[0]
        if self.conf_params['os_deps']:
            self.conf_params['os_deps'] = self._translate_pkg_to_id('os_deps', self.conf_params['os_deps'].split(','))
        if self.conf_params['pip']:
            self.conf_params['pip'] = self._translate_pkg_to_id('pip', self.conf_params['pip'].split(','))

    def _translate_pkg_to_id(self, pkgtype, pkglist):
        if not os.path.exists(pkgtype):
            raise RuntimeError("{0} file doesn't found, please download from github "
                               "and put it under the same directory as deploy tool".format(pkgtype))
            # uai_logger.info("Start download {0} package info".format(pkgtype))
            # self.conf_params['pkg_type'] = pkgtype
            # self._format_availableenv_param()
            # self.cmd_url = UCLOUD_API_URL
            # self._cmd_writefile_package(pkgtype)
            
        resultlist = []
        uai_logger.info("Start translate {0} package to their id, packages: {1}".format(pkgtype, pkglist))
        for avpkg in  json.load(open(pkgtype), 'utf-8'):
            for pkg in pkglist:
                if pkgtype=='os' or pkgtype=='language' or pkgtype=='ai_arch':
                    versionsplit = pkg.rfind('-')
                    if versionsplit >= 0:
                        if avpkg["PkgName"] == pkg[:versionsplit] and (avpkg["PkgVersion"] == "" or avpkg["PkgVersion"] == pkg[versionsplit+1:]):
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

        if len(pkglist) != 0:
            uai_logger.error("Some {0} package is not supported: {1}".format(pkgtype, pkglist))
            raise RuntimeError("Some {0} package is not supported: {1}".format(pkgtype, pkglist))

        uai_logger.info("End translate {0} package to their id, result: {1}".format(pkgtype, resultlist))
        return resultlist

    def parse_ufile_url(self, url):
        bucket = url[url.find('://') + 3: url.find('.')]
        parturl = url.split('.ufileos.com/')
        if len(parturl) > 1:
            region = parturl[0][parturl[0].find('.') + 1: ]
        if url.find('?') > 0:
            filename = url[url.rfind('/') + 1: url.find('?')]
        else:
            filename = url[url.rfind('/') + 1:]

        return bucket, filename


    def _format_deploy_param(self):
        self.translate_pkg_params()
        self.cmd_params['ServiceID'] = self.conf_params['service_id']
        self.cmd_params['OSVersion'] = self.conf_params['os']
        self.cmd_params['PythonVersion'] = self.conf_params['language']
        self.cmd_params['AIFrameVersion'] = self.conf_params['ai_arch_v']
        self.cmd_params['UfileBucket'], self.cmd_params['UfileName'] = self.parse_ufile_url(self.conf_params['ufile_url'])
        self.cmd_params['UfileURL'] = self.conf_params['ufile_url']
        if self.conf_params['os_deps']:
            i = 0
            for aptgetid in self.conf_params['os_deps']:
                self.cmd_params['AptGetPKGID.' + str(i) ] = aptgetid
                i = i + 1
        else:
            self.cmd_params['AptGetPKGID.0'] = ''
        if self.conf_params['pip']:
            i = 0
            for pipid in self.conf_params['pip']:
                self.cmd_params['PipPKGID.' + str(i) ] = pipid
                i = i + 1
        else:
            self.cmd_params['PipPKGID.0'] = ''
        self.cmd_params['DeployWeight'] = self.conf_params['deploy_weight']
        self.cmd_params['Action'] = 'DeployUAIService'

    def _format_checkprogress_param(self):
        self.cmd_params['Action'] = 'CheckUAIDeployProgress'
        self.cmd_params['ServiceID'] = self.conf_params['service_id']
        self.cmd_params['SrvVersion'] = self.conf_params['service_version']

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
        self.rsp = json.loads(r.text, encoding='utf-8')
        if self.rsp["RetCode"] != 0:
            uai_logger.error("{0} Fail: [{1}]{2}".format(self.cmd_params["Action"], self.rsp["RetCode"], self.rsp["Message"].encode('utf-8')))
            raise RuntimeError("{0} Fail: [{1}]{2}".format(self.cmd_params["Action"], self.rsp["RetCode"], self.rsp["Message"].encode('utf-8')))
        else:
            del self.rsp['Action']
            uai_logger.info("{0} Success: {1}".format(self.cmd_params["Action"], get_response(self.rsp,0)))

    def cmd(self):
        """ Create the task of specified task id
        """
        # if self.conf_params:
        self._load_args()
        self._format_request_param()
        self._cmd_request()