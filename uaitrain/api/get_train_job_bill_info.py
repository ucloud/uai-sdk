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

class GetUAITrainBillInfoOp(BaseUAITrainAPIOp):
    ACTION_NAME = "GetUAITrainBillInfo"
    """
    GetUAITrainBillInfoOp
        Compatable with UAI Train GetUAITrainBillInfo API func
        Input:
            pub_key             string(required) Public key of the user
            priv_key            string(required) Private key of the user
            project_id          int(optional)    Project ID of the job
            region              string(optional) Which Region to run the job
            zone                string(optional) Which Zone in the Region to run the job
            beg_time        string(required) the start time of bill
            end_time        string(required) the end time of bill
            offset          int(optional) the offset of list
            limit           int(optional) the max num of returned list, return all bill list if isn't set

        Output:
            RetCode                 int(required)             Op return code: 0: success, others: error code
            TotalCount              string(required)          the count of result
            TotalExecuteTime        int(required)             total exec time of all train job
            TotalPrice              int(required)             total price of all train job
            Message                 string(not required)      Message: error description
            DataSet                 []                        the detailed bill information of train job
    """

    def __init__(self, pub_key, priv_key, beg_time, end_time, offset="", limit="", project_id="", region="", zone=""):
        super(GetUAITrainBillInfoOp, self).__init__(self.ACTION_NAME,
                                                     pub_key,
                                                     priv_key,
                                                     project_id,
                                                     region,
                                                     zone)
        self.cmd_params["BeginTime"] = beg_time
        self.cmd_params["EndTime"] = end_time
        self.cmd_params["Offset"] = offset
        self.cmd_params["Limit"] = limit

    def _check_args(self):
        super(GetUAITrainBillInfoOp, self)._check_args()
        if self.cmd_params["BeginTime"] == "" or type(self.cmd_params["BeginTime"]) != int:
            raise RuntimeError("beg_time shoud be <int> and is not nil.")
        if self.cmd_params["EndTime"] == "" or type(self.cmd_params["EndTime"]) != int:
            raise RuntimeError("end_time shoud be <int> and is not nil.")

        if self.cmd_params["BeginTime"] > self.cmd_params["EndTime"]:
            raise RuntimeError("end_time should be  greater than beg_time. end_time: {0}, beg_time: {1}".
                               format(self.cmd_params["EndTime"], self.cmd_params["BeginTime"]))
