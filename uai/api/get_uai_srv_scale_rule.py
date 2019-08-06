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

from uai.utils.utils import val_to_str
from uai.utils.logger import uai_logger
from uai.api.base_api import BaseUaiServiceApiOp

class GetUAISrvScaleRuleApiOp(BaseUaiServiceApiOp):

    ACTION_NAME = "GetUAISrvScaleRule"
    """
        Input:
            public_key          string(required) Public key of the user
            private_key         string(required) Private key of the user
            project_id          int(optional)    Project ID of the job
            region              string(optional) Which Region to run the job
            zone                string(optional) Which Zone in the Region to run the job
            ServiceID         list(required) the metric list, you can get it from DescribeResourceMetric api.

        Output:
            RetCode         int(required)                Op return code: 0: success, others: error code
            TotalCount      string(required)             the count of result
            Message         string(not required)         Message: error description
            Result         []ScaleRule                           the detailed information of metric
            
        ScaleRule:
            MetricID      int
            MetricName    string
            MaxNode       int
            MinNode       int
            UpThreshold   float
            DownThreshold float
            EnableStandby bool
            CreateTime    int
            ModifyTime    int
            Status        string
    """
    def __init__(self, public_key, private_key, service_id, project_id='', region=''):
        super(GetUAISrvScaleRuleApiOp, self).__init__(self.ACTION_NAME, public_key, private_key, project_id, region, zone=False)
        self.cmd_params['Region'] = region if region != '' else super(GetUAISrvScaleRuleApiOp, self).PARAMS_DEFAULT_REGION
        self.cmd_params['ServiceID'] = service_id

    def _check_args(self, params):
        if params["ServiceID"] == "" or type(params["ServiceID"]) != str:
            uai_logger.error("ServiceID should be <str> and is not nil.")
            return False
        return True

    def call_api(self):
        succ, self.rsp = super(GetUAISrvScaleRuleApiOp, self).call_api()
        return succ, self.rsp
