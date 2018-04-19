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

class CreateUAITrainJobOp(BaseUAITrainAPIOp):
    ACTION_NAME = "CreateUAITrainJob"
    """
    CreateUAITrainJobOp
        Compatable with UAI Train CreateUAITrainJob API func
        Input:
            pub_key             string(required) Public key of the user
            priv_key            string(required) Private key of the user
            project_id          int(optional)    Project ID of the job
            region              string(optional) Which Region to run the job
            zone                string(optional) Which Zone in the Region to run the job
            job_name            string(required) Job name of the job
            work_id             int(required) the id of train node, you can get detail info from GetUAITrainAvailableResourceOp.
                                                1860001, include 1 GPU
                                                1860003, include 4 GPU
                                                etc.
            code_uhub_path      string(required) Which image in the uhub to run the job
            data_ufile_path     string(required) the ufile path of input data
            out_ufile_path      string(required) the ufile path of output data
            docker_cmd          string(required) the cmd of run the job
            max_exec_time       int(required) the max exec time of job. if the job don't finish in the time, system will stop the job.
            work_num            int(optional) the num of server. This param should be greater than 1 for distributed train.
            dist_ai_frame       int(optional) the frame of distributed train 
            business_group      string(optional) Which business group to run the job
            job_memo            string(optional) the memo of the job
            
        Output:
            RetCode       int(required)                Op return code: 0: success, others: error code
            TrainJObID    string(required)             the id of the train job
            Message       string(not required)         Message: error description

    """

    def __init__(self, pub_key, priv_key, job_name, work_id, code_uhub_path, data_ufile_path, out_ufile_path,
                 docker_cmd, max_exec_time, work_num=1, dist_ai_frame="", business_group="", job_memo="", project_id="",
                 region="", zone=""):
        super(CreateUAITrainJobOp, self).__init__(self.ACTION_NAME,
                                                     pub_key,
                                                     priv_key,
                                                     project_id,
                                                     region,
                                                     zone)
        self.cmd_params["TrainJobName"] = job_name
        self.cmd_params["TrainWorkId"] = work_id
        self.cmd_params["CodeUhubPath"] = code_uhub_path
        self.cmd_params["DataUfilePath"] = data_ufile_path
        self.cmd_params["OutputUfilePath"] = out_ufile_path
        self.cmd_params["DockerCmd"] = docker_cmd
        self.cmd_params["PredictStartTime"] = 0
        self.cmd_params["MaxExecuteTime"] = max_exec_time
        self.cmd_params["TrainWorkAmount"] = work_num
        self.cmd_params["DistAIFrame"] = dist_ai_frame

        self.cmd_params["TrainPublicKey"] = pub_key
        self.cmd_params["TrainPrivateKey"] = priv_key

        self.cmd_params["TrainJobMemo"] = job_memo
        self.cmd_params["BusinessGroup"] = business_group


    def _check_args(self):
        super(CreateUAITrainJobOp, self)._check_args()
        if self.cmd_params["TrainJobName"] == "" or type(self.cmd_params["TrainJobName"]) != str:
            raise RuntimeError("job_name shoud be <str> and is not nil.")

        if self.cmd_params["TrainWorkId"] == "" or type(self.cmd_params["TrainWorkId"]) != int:
            raise RuntimeError("work_id shoud be <int> and is not nil.")

        if self.cmd_params["CodeUhubPath"] == "" or type(self.cmd_params["CodeUhubPath"]) != str:
            raise RuntimeError("code_uhub_path shoud be <str> and is not nil.")

        if self.cmd_params["DataUfilePath"] == "" or type(self.cmd_params["DataUfilePath"]) != str:
            raise RuntimeError("data_ufile_path shoud be <str> and is not nil.")

        if self.cmd_params["OutputUfilePath"] == "" or type(self.cmd_params["OutputUfilePath"]) != str:
            raise RuntimeError("out_ufile_path shoud be <str> and is not nil.")

        if self.cmd_params["DockerCmd"] == "" or type(self.cmd_params["DockerCmd"]) != str:
            raise RuntimeError("docker_cmd shoud be <str> and is not nil.")

        if self.cmd_params["MaxExecuteTime"] == "" or type(self.cmd_params["MaxExecuteTime"]) != int:
            raise RuntimeError("max_exec_time shoud be <int> and is not nil.")

        if self.cmd_params["TrainWorkAmount"] == "" or type(self.cmd_params["TrainWorkAmount"]) != int:
            raise RuntimeError("max_exec_time shoud be <int> and is not nil.")