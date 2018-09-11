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


class ModifyUAITrainJobNameApiOp(BaseUAITrainAPIOp):
    """
    ModifyUAITrainJobNameAPI

        Identical with UAI Train ModifyUAITrainJobName API func
        Input:
            TrainJobId           string(required)        the id of train job
            TrainJobName         string(required)        the memo of train job
    """
    ACTION_NAME = "ModifyUAITrainJobName"

    def __init__(self, pub_key, priv_key, job_id, job_name, project_id="", region="", zone=""):
        super(ModifyUAITrainJobNameApiOp, self).__init__(self.ACTION_NAME, pub_key, priv_key, project_id, region, zone)
        self.cmd_params["TrainJobId"] = job_id
        self.cmd_params["TrainJobName"] = job_name

    def _check_args(self):
        super(ModifyUAITrainJobNameApiOp, self)._check_args()

        if self.cmd_params["TrainJobId"] == "" or type(self.cmd_params["TrainJobId"]) != str:
            raise ValueError("TrainJobId should be <str> and should not be nil")

        if self.cmd_params["TrainJobName"] == "" or type(self.cmd_params["TrainJobName"]) != str:
            raise ValueError("TrainJobName should be <str> and should not be nil")
