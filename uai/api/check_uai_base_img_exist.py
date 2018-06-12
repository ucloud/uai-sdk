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

class CheckUAIBaseImgExistApiOp(BaseUaiServiceApiOp):

    ACTION_NAME = "CheckUAIBaseImgExist"

    def __init__(self, public_key, private_key, os_version, python_version, ai_frame_version, os_deps='', pip='', project_id='', region='', zone=''):
        super(CheckUAIBaseImgExistApiOp, self).__init__(self.ACTION_NAME, public_key, private_key, project_id, region, zone)
        self.cmd_params['Region'] = region if region != '' else super(CheckUAIBaseImgExistApiOp, self).PARAMS_DEFAULT_REGION
        self.cmd_params['OSVersion'] = os_version
        self.cmd_params['PythonVersion'] = python_version
        self.cmd_params['AIFrameVersion'] = ai_frame_version

        self._get_pkgs(os_deps, 'AptGetPKGID')
        self._get_pkgs(pip, 'PipPKGID')

    def _check_args(self, params):
        if params['OSVersion'] == '':
            return False
        if params['PythonVersion'] == '':
            return False
        if params['AIFrameVersion'] == '':
            return False
        return True

    def call_api(self):
        succ, self.rsp = super(CheckUAIBaseImgExistApiOp, self).call_api()
        return succ, self.rsp
