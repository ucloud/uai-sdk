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

class UpdateUAISrvScaleRuleApiOp(BaseUaiServiceApiOp):

    ACTION_NAME = "UpdateUAISrvScaleRuleParams"
    """
        Input:
            public_key          string(required) Public key of the user
            private_key         string(required) Private key of the user
            project_id          int(optional)    Project ID of the job
            region              string(optional) Which Region to run the job
            zone                string(optional) Which Zone in the Region to run the job
            
            ServiceID     string
            MetricID      int
            MaxNode       int
            MinNode       int
            UpThreshold   float
            DownThreshold float
            EnableStandby bool

        Output:
            RetCode         int(required)                Op return code: 0: success, others: error code
            TotalCount      string(required)             the count of result
            Message         string(not required)         Message: error description            
    """
    def __init__(self, public_key, private_key, service_id, metric_id, max_node, min_node, up_threshold, down_threshold,
                 enable_standby, project_id='', region=''):

        super(UpdateUAISrvScaleRuleApiOp, self).__init__(self.ACTION_NAME, public_key, private_key, project_id, region, zone=False)
        self.cmd_params['Region'] = region if region != '' else super(UpdateUAISrvScaleRuleApiOp, self).PARAMS_DEFAULT_REGION
        self.cmd_params['ServiceID'] = service_id
        self.cmd_params['MetricID'] = metric_id
        self.cmd_params['MaxNode'] = max_node
        self.cmd_params['MinNode'] = min_node
        self.cmd_params['UpThreshold'] = up_threshold
        self.cmd_params['DownThreshold'] = down_threshold
        self.cmd_params['EnableStandby'] = enable_standby

    def _check_args(self, params):
        if params["ServiceID"] == "" or type(params["ServiceID"]) != str:
            uai_logger.error("ServiceID should be <str> and is not nil.")
            return False
        if params["MetricID"] == "" or type(params["MetricID"]) != int:
            uai_logger.error("MetricID should be <int> and is not nil.")
            return False
        if params["MaxNode"] == "" or type(params["MaxNode"]) != int:
            uai_logger.error("MaxNode should be <int> and is not nil.")
            return False
        if params["MinNode"] == "" or type(params["MinNode"]) != int:
            uai_logger.error("MinNode should be <int> and is not nil.")
            return False
        if params["UpThreshold"] == "":
            uai_logger.error("UpThreshold should be <float> and is not nil.")
            return False
        if params["DownThreshold"] == "":
            uai_logger.error("DownThreshold should be <float> and is not nil.")
            return False
        if params["EnableStandby"] == "" or type(params["EnableStandby"]) != bool:
            uai_logger.error("EnableStandby should be <bool> and is not nil.")
            return False

        params['EnableStandby'] = 'true' if params["EnableStandby"] is True else 'false'
        return True

    def call_api(self):
        succ, self.rsp = super(UpdateUAISrvScaleRuleApiOp, self).call_api()
        return succ, self.rsp
