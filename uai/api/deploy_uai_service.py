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

class DeployUAIServiceApiOp(BaseUaiServiceApiOp):

    ACTION_NAME = "DeployUAIService"

    def __init__(self, public_key, private_key, service_id,ufile_url, os_version='', python_version='', ai_frame_version='',  bimg_name='',
                 apt_list='', pip_list='', project_id='', region='', zone=''):
        super(DeployUAIServiceApiOp, self).__init__(self.ACTION_NAME, public_key, private_key, project_id, region, zone)
        self.cmd_params['Region'] = region if region != '' else super(DeployUAIServiceApiOp, self).PARAMS_DEFAULT_REGION
        self.cmd_params['ServiceID'] = service_id

        self.cmd_params['OSVersion'] = os_version
        self.cmd_params['PythonVersion'] = python_version
        self.cmd_params['AIFrameVersion'] = ai_frame_version

        self.cmd_params['BimgName'] = bimg_name

        self.cmd_params['UfileBucket'],\
        self.cmd_params['UfileName'] = self.parse_ufile_url(ufile_url)
        self.cmd_params['UfileURL'] = ufile_url

        self._get_pkgs(apt_list, 'AptGetPKGID')
        self._get_pkgs(pip_list, 'PipPKGID')

    def parse_ufile_url(self, url):
        bucket = url[url.find('://') + 3: url.find('.')]
        if url.find('?') > 0:
            filename = url[url.rfind('/') + 1: url.find('?')]
        else:
            filename = url[url.rfind('/') + 1:]

        return bucket, filename

    def _check_args(self, params):
        if params['ServiceID'] == '':
            return False
        if params['UfileURL'] == '':
            return False
        if params['BimgName'] == '':
            if params['OSVersion'] == '' or params['PythonVersion'] == '' or params['AIFrameVersion'] == '':
                return False
        return True

    def call_api(self):
        succ, rsp = super(DeployUAIServiceApiOp, self).call_api()
        return succ, rsp