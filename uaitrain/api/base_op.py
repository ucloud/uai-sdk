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
from uai.utils.logger import uai_logger
from uai.utils.retcode_checker import *

DEFAULT_UCLOUD_API_URL = 'http://api.ucloud.cn'
DEFAULT_UAI_TRAIN_REGION = 'cn-bj2'
DEFAULT_UAI_TRAIN_ZONE = 'cn-bj2-04'

# DEFAULT_UCLOUD_API_URL = 'http://api.pre.ucloudadmin.com'
# DEFAULT_UAI_TRAIN_REGION = 'pre'
# DEFAULT_UAI_TRAIN_ZONE = 'pre'

PARAM_ACTION = 'Action'
PARAM_PUBLIC_KEY = 'PublicKey'
PARAM_PROJECT_ID = 'ProjectId'
PARAM_REGION = 'Region'
PARAM_ZONE = 'Zone'

class BaseUAITrainAPIOp(object):
    """ The Base api for uai Train
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
        if self.cmd_params.has_key('Signature'):
            self.cmd_params.pop('Signature')
        self.cmd_params['Signature'] = _verfy_ac(self.priv_key,
                                                 self.cmd_params)
        print (self.cmd_params)
        uai_logger.info("Call http request: {0} ".format(get_request(self.cmd_url, params=self.cmd_params)))
        r = requests.get(self.cmd_url, params=self.cmd_params)
        rsp = json.loads(r.text, 'utf-8')
        if rsp['RetCode'] != 0:
            uai_logger.error("{0} Fail: [{1}]{2}".format(self.cmd_params[PARAM_ACTION], rsp['RetCode'],
                                                         rsp['Message'].encode('utf-8')))
            return False, rsp
        else:
            del rsp[PARAM_ACTION]
            #uai_logger.info("{0} Success: {1}".format(self.cmd_params[PARAM_ACTION], get_response(rsp, 0)))
            return True, rsp
        # add other operations in subclasses#

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