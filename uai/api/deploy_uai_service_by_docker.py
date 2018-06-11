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

from uai.api.base_api import BaseUaiServiceApiOp

class DeployUAIServiceByDockerApiOp(BaseUaiServiceApiOp):

    ACTION_NAME = "DeployUAIServiceByDocker"

    def __init__(self, public_key, private_key, service_id, image_name, deploy_weight='', srv_v_info='', project_id='', region='', zone=''):
        super(DeployUAIServiceByDockerApiOp, self).__init__(self.ACTION_NAME, public_key, private_key, project_id, region, zone)
        self.cmd_params['Region'] = region if region != '' else super(DeployUAIServiceByDockerApiOp, self).PARAMS_DEFAULT_REGION
        self.cmd_params['ServiceID'] = service_id

        self.cmd_params['UimgName'] = image_name
        self.cmd_params['DeployWeight'] = deploy_weight
        self.cmd_params['SrvVerMemo'] = srv_v_info


    def _check_args(self, params):
        if params['ServiceID'] == '':
            return False
        if params['UimgName'] == '':
            return False
        if 'DeployWeight' in params and params['DeployWeight'] != '':
            if int(params['DeployWeight']) < 1 or int(params["DeployWeight"]) > 100:
                print ('deploy_weight should be int between 1 to 100, but now:{0}'.format(params['DeployWeight']))
                return False
        return True

    def call_api(self):
        succ, rsp = super(DeployUAIServiceByDockerApiOp, self).call_api()
        return succ, rsp