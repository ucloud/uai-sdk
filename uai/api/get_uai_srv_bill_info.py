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

class GetUAISrvBillInfoApiOp(BaseUaiServiceApiOp):

    ACTION_NAME = "GetUAISrvBillInfo"

    def __init__(self, public_key, private_key, begin_time, end_time, project_id='', region='', zone='', offset=0, limit=0):
        super(GetUAISrvBillInfoApiOp, self).__init__(self.ACTION_NAME, public_key, private_key, project_id, region, zone)
        self.cmd_params['Region'] = region if region != '' else super(GetUAISrvBillInfoApiOp, self).PARAMS_DEFAULT_REGION
        self.cmd_params['BeginTime'] = begin_time
        self.cmd_params['EndTime'] = end_time

        self.cmd_params['Offset'] = offset
        self.cmd_params['Limit'] = limit

    def _check_args(self, params):
        if params['BeginTime'] == '':
            return False
        if params['EndTime'] == '':
            return False

        return True

    def call_api(self):
        succ, self.rsp = super(GetUAISrvBillInfoApiOp, self).call_api()
        return succ, self.rsp