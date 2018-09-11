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


class GetUAITrainAvailableBackendApiOp(BaseUAITrainAPIOp):
    """
    GetUAITrainAvailableBackendAPI

        Identical with UAI Train GetUAITrainAvailableBackend API func
        Input:
            TrainModeId     int         train mode info
        Output:
            DataItem        Array       []DataBackendInfo
    """
    ActionName = "GetUAITrainAvailableBackend"

    def __init__(self, train_mode, pub_key, priv_key, project_id="", region="", zone=""):
        super(GetUAITrainAvailableBackendApiOp, self).__init__(self.ActionName, pub_key, priv_key, project_id, region, zone)
        self.cmd_params["TrainModeId"] = train_mode

    def _check_args(self):
        super(GetUAITrainAvailableBackendApiOp, self)._check_args()
        if self.cmd_params["TrainModeId"] == "" or type(self.cmd_params["TrainModeId"]) != int:
            raise ValueError("TrainModeId should be <int> and should not be nil")
