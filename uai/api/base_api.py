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

import json
import requests
from uai.utils.utils import _verfy_ac
from uai.utils.retcode_checker import *

class BaseUaiServiceApiOp(object):
    """ The Base api for uai Service
    """
    UCLOUD_API_URL = 'http://api.ucloud.cn'
    PARAMS_DEFAULT_REGION = "cn-bj2"
    PARAMS_DEFAULT_ZONE = "cn-bj2-04"

    PARAMS_DEFAULT_BUSINESSGROUP = "Default"
    PACKAGE_TYPE = {'os': 'OS', 'language': 'Python', 'ai_arch': 'AIFrame', 'os_deps': 'AptGet', 'pip': 'Pip'}

    def __init__(self, action, public_key, private_key, project_id='', region='', zone=''):
        self.action = action
        self.public_key = public_key
        self.private_key = private_key
        self.project_id = project_id
        self.region = self.PARAMS_DEFAULT_REGION if region == '' else region
        self.zone = self.PARAMS_DEFAULT_ZONE if zone == '' else zone

        self.cmd_params = {}
        self.cmd_params['Action'] = self.action
        self.cmd_params['PublicKey'] = self.public_key
        self.cmd_params['Region'] = self.region
        if self.zone is not False:
            self.cmd_params['Zone'] = self.zone
        if self.project_id != '':
            self.cmd_params['ProjectId'] = self.project_id
        self.cmd_url = self.UCLOUD_API_URL

    def _check_args(self, params):
        pass

    def _cmd_common_request(self):
        if 'Signature' in self.cmd_params:
            self.cmd_params.pop('Signature')
        self.cmd_params['Signature'] = _verfy_ac(self.private_key,
                                                 self.cmd_params)
        uai_logger.info("Call http request: {0} ".format(get_request(self.cmd_url, params=self.cmd_params)))
        r = requests.get(self.cmd_url, params=self.cmd_params)
        print(r.text)
        self.rsp = json.loads(r.text, encoding="utf-8")
        if self.rsp["RetCode"] != 0:
            uai_logger.error("{0} Fail: [{1}]{2}".format(self.cmd_params["Action"], self.rsp["RetCode"],
                                                         self.rsp["Message"].encode('utf-8')))
            return False
        else:
            del self.rsp['Action']
            uai_logger.info("{0} Success: {1}".format(self.cmd_params["Action"], get_response(self.rsp, 0)))
            return True

    def _get_pkgs(self, pkgids, pkgname):
        if pkgids == '':
            self.cmd_params[pkgname + '.' + '0'] = ''
            return
        pkgs = pkgids.split(',')
        i = 0
        for pkg in pkgs:
            self.cmd_params[pkgname + '.' + str(i)] = pkg
            i += 1
        return

    def call_api(self):
        if self._check_args(self.cmd_params) == False:
            raise RuntimeError("Check API params error, params: {0}".format(self.cmd_params))
        succ = self._cmd_common_request()
        return succ, self.rsp