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


class GetUAITrainRunningLogApiOp(BaseUAITrainAPIOp):
    """
    GetUAITrainRunningLogAPI

        Identical with UAI Train GetUAITrainRunningLog API func
        Input:
            TrainJobId          string(required)            Job id of the job
            LogTopicId          string(required)            log topic id
        Output:
            RunningLog          []string                     realtime log that train job produces
    """
    ACTION_NAME = "GetUAITrainRunningLog"

    def __init__(self, pub_key, priv_key, job_id, log_topic_id, project_id="", region="", zone=""):
        super(GetUAITrainRunningLogApiOp, self).__init__(self.ACTION_NAME, pub_key, priv_key, project_id, region, zone)
        self.cmd_params["TrainJobId"] = job_id
        self.cmd_params["LogTopicId"] = log_topic_id

    def _check_args(self):
        super(GetUAITrainRunningLogApiOp, self)._check_args()

        if self.cmd_params["TrainJobId"] == "" or type(self.cmd_params["TrainJobId"]) != str:
            raise ValueError("TrainJobId should be <str> and should not be nil.")
        if self.cmd_params["LogTopicId"] == "" or type(self.cmd_params["LogTopicId"]) != str:
            raise ValueError("LogTopicId should be <str> and should not be nil.")
