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


class CreateUAITrainJobApiOp(BaseUAITrainAPIOp):
    """
    CreateUAITrainJobAPI

        Identical with UAI Train CreateUAITrainJob API func
        Input:
            TrainJobName               string
            TrainWorkId                int
            CodeUhubPath               string
            DataUfilePath              string
            InputDataBackendId         int
            OutputUfilePath            string
            OutputDataBackendId        int
            DockerCmd                  string
            MaxExecuteTime             int
            TrainWorkAmount            int(not required)
            TrainModeId                int
            DistAIFrame                int(not required)
            TrainPublicKey             string
            TrainPrivateKey            string
            TrainJobMemo               string(not required)
            BusinessGroup              string(not required)
        Output:
            TrainJobId                 string                 created train job id
    """
    ACTION_NAME = "CreateUAITrainJob"

    def __init__(self, pub_key, priv_key, job_name, work_node, image_path, input_path, input_backend,
                 output_path, output_backend, docker_cmd, max_exec_time,train_mode, work_amount=1, dist_ai_frame=0,
                 business_group="", job_memo="", project_id="", region="", zone=""):
        super(CreateUAITrainJobApiOp, self).__init__(self.ACTION_NAME, pub_key, priv_key, project_id, region, zone)
        self.cmd_params["TrainJobName"] = job_name
        self.cmd_params["TrainWorkId"] = work_node
        self.cmd_params["CodeUhubPath"] = image_path
        self.cmd_params["DataUfilePath"] = input_path
        self.cmd_params["InputDataBackendId"] = input_backend
        self.cmd_params["OutputUfilePath"] = output_path
        self.cmd_params["OutputDataBackendId"] = output_backend
        self.cmd_params["DockerCmd"] = docker_cmd
        self.cmd_params["MaxExecuteTime"] = max_exec_time
        self.cmd_params["TrainWorkAmount"] = work_amount
        self.cmd_params["TrainModeId"] = train_mode
        self.cmd_params["DistAIFrame"] = dist_ai_frame
        self.cmd_params["TrainPublicKey"] = pub_key
        self.cmd_params["TrainPrivateKey"] = priv_key
        self.cmd_params["TrainJobMemo"] = job_memo
        self.cmd_params["BusinessGroup"] = business_group

    def _check_args(self):
        super(CreateUAITrainJobApiOp, self)._check_args()
        if self.cmd_params["TrainJobName"] == "" or type(self.cmd_params["TrainJobName"]) != str:
            raise ValueError("TrainJobName should be <str> and should not be nil.")

        if self.cmd_params["TrainWorkId"] == "" or type(self.cmd_params["TrainWorkId"]) != int:
            raise ValueError("TrainWorkId should be <int> and should not be nil.")

        if self.cmd_params["CodeUhubPath"] == "" or type(self.cmd_params["CodeUhubPath"]) != str:
            raise ValueError("CodeUhubPath should be <str> and should not be nil.")

        if self.cmd_params["DataUfilePath"] == "" or type(self.cmd_params["DataUfilePath"]) != str:
            raise ValueError("DataUfilePath should be <str> and should not be nil.")

        if self.cmd_params["InputDataBackendId"] == "" or type(self.cmd_params["InputDataBackendId"]) != int:
            raise ValueError("InputDataBackendId should be <int> and not nil")

        if self.cmd_params["OutputUfilePath"] == "" or type(self.cmd_params["OutputUfilePath"]) != str:
            raise ValueError("OutputUfilePath should be <str> and should not be nil.")

        if self.cmd_params["OutputDataBackendId"] == "" or type(self.cmd_params["OutputDataBackendId"]) != int:
            raise ValueError("OutputDataBackendId should be <int> and not nil")

        if self.cmd_params["DockerCmd"] == "" or type(self.cmd_params["DockerCmd"]) != str:
            raise ValueError("DockerCmd should be <str> and should not be nil.")

        if self.cmd_params["MaxExecuteTime"] == "" or type(self.cmd_params["MaxExecuteTime"]) != int:
            raise ValueError("MaxExecuteTime should be <int> and should not be nil.")

        if self.cmd_params["TrainWorkAmount"] == "" or type(self.cmd_params["TrainWorkAmount"]) != int:
            raise ValueError("TrainWorkAmount should be <int> and should not be nil.")

        if self.cmd_params["TrainModeId"] == "" or type(self.cmd_params["TrainModeId"]) != int:
            raise ValueError("TrainModeId should be <int> and should not be nill")
