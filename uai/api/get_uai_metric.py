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

class GetUAIServiceMetricApiOp(BaseUaiServiceApiOp):

    ACTION_NAME = "GetMetric"
    """
    GetMetric
        Input:
            public_key          string(required) Public key of the user
            private_key         string(required) Private key of the user
            project_id          int(optional)    Project ID of the job
            region              string(optional) Which Region to run the job
            zone                string(optional) Which Zone in the Region to run the job
            metric_list         list(required) the metric list, you can get it from DescribeResourceMetric api.
            beg_time            int(required) the begin time of metric info.(unix time)
            end_time            int(required) the begin time of metric info.(unix time)

        Output:
            RetCode         int(required)                Op return code: 0: success, others: error code
            TotalCount      string(required)             the count of result
            Message         string(not required)         Message: error description
            DataSet         []                           the detailed information of metric
    """
    def __init__(self, public_key, private_key, service_id, metric_list, beg_time, end_time, project_id='', region=''):
        super(GetUAIServiceMetricApiOp, self).__init__(self.ACTION_NAME, public_key, private_key, project_id, region, zone=False)
        self.cmd_params['Region'] = region if region != '' else super(GetUAIServiceMetricApiOp, self).PARAMS_DEFAULT_REGION
        self.cmd_params['ResourceType'] = 'uaiservice'
        self.cmd_params['ResourceId'] = service_id
        self.cmd_params['BeginTime'] = beg_time
        self.cmd_params['EndTime'] = end_time

        self._get_pkgs(val_to_str(metric_list), 'MetricName')

    def _check_args(self, params):
        print(params)
        if params["ResourceId"] == "" or type(params["ResourceId"]) != str:
            uai_logger.error("resource_id shoud be <str> and is not nil.")
            return False
        if type(params["BeginTime"]) != int:
            uai_logger.error("beg_time shoud be <int>.")
            return False
        if type(params["EndTime"]) != int:
            uai_logger.error("end_time shoud be <int>.")
            return False
        if params["BeginTime"] > params["EndTime"]:
            uai_logger.error("end_time should be  greater than beg_time. end_time: {0}, beg_time: {1}".
                               format(params["EndTime"], params["BeginTime"]))
            return False
        return True

    def call_api(self):
        uai_logger.warning("Please Call This API:{0} with Console.".format(self.cmd_params['Action']))
        rsp_message = "Please Call This API:{0} with Console.".format(self.cmd_params['Action'])
        return True, rsp_message
