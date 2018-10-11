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


class GetUAITrainJobListApiOp(BaseUAITrainAPIOp):
    """
    GetUAITrainJobListAPI

        Identical with UAI Train GetUAITrainJobList API func
        Input:
            TrainJobId          string(optional)            Which train job to get info
            Offset              int(optional)               the offset of list
            Limit               int(optional)               the max num of returned list, return all job list if isn't set
        Output:
            RetCode             int                         API return code: 0: success, others: error code
            Action              string                      Action name
            Message             string                      Message: error description
            TotalCount          string(required)            the count of result
            DataSet             Array                       UAITrainJob

        UAITrainJob:
            TrainJobId          string                      Id of train job
            TrainJobName        string                      Name of train job
            TrainJobMemo        string                      Memo of train job
            BusinessGroup       string                      business group of train job
            ResourceId          string                      resource id of train job
            CreateTime          int64                       create time of train job
            Status              string                      status of train job
            TrainWorkSrv        []FixedServerNodeInfo       work server info
            TrainPSSrv          []FixedServerNodeInfo       ps server info
            StartTime           int64                       start train time of current train job
            EndTime             int64                       end train time of current train job
            MaxExecuteTime      int64                       max train time
            BillType            string                      bill type id of current train job
            BillUnit            string                      bill unit of current train job, e.g: cent
            BillUnitPrice       int64                       bill unit price of current train job
            BillTotalPrice      int64                       total price of current train job
            CodeUhubPath        string                      path of docker image for training
            DataUfilePath       string                      input data path
            OutputUfilePath     string                      output data path
            DockerCmd           string                      docker run cmd
            LogTensorboardURL   string                      tensorboard url of current train job
            LogFileURL          string                      address of log files
            LogFileBucket       string                      bucket of log files
            DataType            string                      input data backend type
            OutputType          string                      output data backend type
            DistAIFrameItem     DistAIFrameInfo             dist ai frame info

        FixedServerNodeInfo:
            NodeId              int64                       id of current node
            NodeName            string                      name of current node
            NodeType            string                      type of current node
            DiskSize            int64                       disk size of current node
            CPU                 int64                       num of cpu
            Memory              int64                       memory of current node
            AcceleratorName     string                      name of accelerator
            AcceleratorVersion  string                      version of accelerator
            AcceleratorAmount   int64                       amount of accelerator
            UnitPrice           int64                       unit price of current node

        DistAIFrameInfo:
            DistAIFrameId       int                         Id of current dist-ai-framework
            DistAIFrameName     string                      Name of current dist-ai-framework
    """
    ACTION_NAME = "GetUAITrainJobList"

    def __init__(self, pub_key, priv_key, job_id="", offset=0, limit=0, project_id="", region="", zone=""):
        super(GetUAITrainJobListApiOp, self).__init__(self.ACTION_NAME, pub_key, priv_key, project_id, region, zone)
        self.cmd_params["TrainJobId"] = job_id
        self.cmd_params["Offset"] = offset
        self.cmd_params["Limit"] = limit

    def _check_args(self):
        super(GetUAITrainJobListApiOp, self)._check_args()
        if self.cmd_params["Limit"] < 0:
            raise ValueError("Limit should be positive")
        if self.cmd_params["Offset"] <0:
            raise ValueError("Offset should be positive")
        if self.cmd_params["Limit"] < self.cmd_params["Offset"]:
            raise ValueError("Limit should be larger than Offset, current Limit: {0}, Offset: {1}".
                             format(self.cmd_params["Limit"], self.cmd_params["Offset"]) )
