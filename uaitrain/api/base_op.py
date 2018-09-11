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

import requests
import json

from uai.utils.utils import _verfy_ac
from uai.utils.retcode_checker import *

DEFAULT_UCLOUD_API_URL = 'http://api.ucloud.cn'
DEFAULT_UAI_TRAIN_REGION = 'cn-bj2'
DEFAULT_UAI_TRAIN_ZONE = 'cn-bj2-04'

PARAM_ACTION = 'Action'
PARAM_PUBLIC_KEY = 'PublicKey'
PARAM_PROJECT_ID = 'ProjectId'
PARAM_REGION = 'Region'
PARAM_ZONE = 'Zone'


class BaseUAITrainAPIOp(object):
    """
        Base API Class for UAI Train

        General Input and Output for APIs under current Class
        Input:
            PublicKey       string(required)        Public key of the user
            ProjectId       int(optional)           Project ID of the task
            Region          string(optional)        Which Region to run the task
            Zone            string(optional)        Which Zone in the Region to run the task
        Output:
            RetCode         int(required)           Op return code: 0: success, others: error code
            Action          string(required)        Action name
            Message         string(not required)    Message: error description
    """
    def __init__(self, action, pub_key, priv_key, project_id, region, zone):
        self.cmd_params = {}
        self.cmd_params[PARAM_ACTION] = action
        self.cmd_params[PARAM_PUBLIC_KEY] = pub_key

        self.priv_key = priv_key
        self.pub_key = pub_key
        self.cmd_url = DEFAULT_UCLOUD_API_URL

        if project_id != "":
            self.cmd_params[PARAM_PROJECT_ID] = project_id
            
        if region != "":
            self.cmd_params[PARAM_REGION] = region
        else:
            self.cmd_params[PARAM_REGION] = DEFAULT_UAI_TRAIN_REGION
        if zone != "":
            self.cmd_params[PARAM_ZONE] = zone
        else:
            self.cmd_params[PARAM_ZONE] = DEFAULT_UAI_TRAIN_ZONE

        pass

    def _cmd_common_request(self):
        if ('Signature' in self.cmd_params) is True:
            self.cmd_params.pop('Signature')
        self.cmd_params['Signature'] = _verfy_ac(self.priv_key,
                                                 self.cmd_params)
        uai_logger.info("Signature: {0}".format(self.cmd_params['Signature']))
        uai_logger.info(self.cmd_params)
        uai_logger.info("Call http request: {0} ".format(get_request(self.cmd_url, params=self.cmd_params)))
        r = requests.get(self.cmd_url, params=self.cmd_params)
        rsp = json.loads(r.text, encoding='utf-8')
        if rsp['RetCode'] != 0:
            uai_logger.error("{0} Fail: [{1}]{2}".format(self.cmd_params[PARAM_ACTION], rsp['RetCode'],
                                                         rsp['Message'].encode('utf-8')))
            return False, rsp
        else:
            del rsp[PARAM_ACTION]
            return True, rsp

    def _check_args(self):
        if self.pub_key == "":
            raise RuntimeError("Public Key should not be empty")
        if self.priv_key == "":
            raise RuntimeError("Private Key should not be empty")
        if self.cmd_params[PARAM_ACTION] == "":
            raise RuntimeError("Action field should not be empty")

    def call_api(self):
        self._check_args()
        return self._cmd_common_request()

    def check_errcode(self):
        pass
