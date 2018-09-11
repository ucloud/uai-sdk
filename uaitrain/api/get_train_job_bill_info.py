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

from uaitrain.api.base_op import BaseUAITrainAPIOp


class GetUAITrainBillInfoApiOp(BaseUAITrainAPIOp):
    """
    GetUAITrainBillInfoOp

        Identical with UAI Train GetUAITrainBillInfo API func
        Input:
            BeginTime       string(required)        the start time of bill
            EndTime         string(required)        the end time of bill
            Offset          int(optional)           the offset of list
            Limit           int(optional)           the max num of returned list, return all bill list if isn't set
        Output:
            TotalCount              string(required)          the count of result
            TotalExecuteTime        int(required)             total exec time of all train job
            TotalPrice              int(required)             total price of all train job
            DataSet                 []                        the detailed bill information of train job
    """
    ACTION_NAME = "GetUAITrainBillInfo"

    def __init__(self, pub_key, priv_key, beg_time, end_time, offset=0, limit=0, project_id="", region="", zone=""):
        super(GetUAITrainBillInfoApiOp, self).__init__(self.ACTION_NAME, pub_key, priv_key, project_id, region, zone)
        self.cmd_params["BeginTime"] = beg_time
        self.cmd_params["EndTime"] = end_time
        self.cmd_params["Offset"] = offset
        self.cmd_params["Limit"] = limit

    def _check_args(self):
        super(GetUAITrainBillInfoApiOp, self)._check_args()
        if self.cmd_params["BeginTime"] == "" or type(self.cmd_params["BeginTime"]) != int:
            raise ValueError("beg_time should be <int> and should not be nil")
        if self.cmd_params["EndTime"] == "" or type(self.cmd_params["EndTime"]) != int:
            raise ValueError("end_time should be <int> and should not be nil")

        if self.cmd_params["BeginTime"] > self.cmd_params["EndTime"]:
            raise ValueError("EndTime should be  greater than BeginTime. EndTime: {0}, BeginTime: {1}".
                               format(self.cmd_params["EndTime"], self.cmd_params["BeginTime"]))
        
        if self.cmd_params["Limit"] < 0:
            raise ValueError("Limit should be positive")
        if self.cmd_params["Offset"] <0:
            raise ValueError("Offset should be positive")
        if self.cmd_params["Limit"] < self.cmd_params["Offset"]:
            raise ValueError("Limit should be larger than Offset, current Limit: {0}, Offset: {1}".
                             format(self.cmd_params["Limit"], self.cmd_params["Offset"]) )
