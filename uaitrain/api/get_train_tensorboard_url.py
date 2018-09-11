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


class GetUAITrainTensorboardUrlApiOp(BaseUAITrainAPIOp):
    """
    GetUAITrainTensorboardUrlAPI

        Identical with UAI Train GetUAITrainTensorboardUrl API func
        Input:
            TrainJobId              string              train job id
        Output:
            TensorboardURL          string              tensorboard url
    """
    ACTION_NAME = "GetUAITrainTensorboardUrl"

    def __init__(self, pub_key, priv_key, job_id, project_id="", region="", zone=""):
        super(GetUAITrainTensorboardUrlApiOp, self).__init__(self.ACTION_NAME, pub_key, priv_key, project_id, region, zone)
        self.cmd_params["TrainJobId"] = job_id

    def _check_args(self):
        super(GetUAITrainTensorboardUrlApiOp, self)._check_args()

        if self.cmd_params["TrainJobId"] == "" or type(self.cmd_params["TrainJobId"]) != str:
            raise ValueError("TrainJobId should be <str> and should not be nil")
