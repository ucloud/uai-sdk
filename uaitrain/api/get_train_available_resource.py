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


class GetUAITrainAvailableResourceApiOp(BaseUAITrainAPIOp):
    """
    GetUAITrainAvailableResourceAPI

        Identical with UAI Train GetUAITrainAvailableResource API func
        Input:
            NodeType           string(optional)         the type of node, default is 'Work' ('Work':train node, 'PS':param node)
            TrainModeId        int(required)            id of current train mode
        Output:
            RetCode            int                      API return code: 0: success, others: error code
            Action             string                   Action name
            Message            string                   Message: error description
            DataSet            Array                    []FixedServerNodeInfo

        FixedServerNodeInfo:
            NodeId              int64                   id of current node
            NodeName            string                  name of current node
            NodeType            string                  type of current node
            DiskSize            int64                   disk size of current node
            CPU                 int64                   num of cpu
            Memory              int64                   memory of current node
            AcceleratorName     string                  name of accelerator
            AcceleratorVersion  string                  version of accelerator
            AcceleratorAmount   int64                   amount of accelerator
            UnitPrice           int64                   unit price of current node
    """
    ACTION_NAME = "GetUAITrainAvailableResource"

    def __init__(self, train_mode, pub_key, priv_key, node_type='Work', project_id="", region="", zone=""):
        super(GetUAITrainAvailableResourceApiOp, self).__init__(self.ACTION_NAME, pub_key, priv_key, project_id, region, zone)
        self.cmd_params["NodeType"] = node_type
        self.cmd_params["TrainModeId"] = train_mode

    def _check_args(self):
        super(GetUAITrainAvailableResourceApiOp, self)._check_args()
        if self.cmd_params["NodeType"] != "Work" and self.cmd_params["NodeType"] != "PS":
            raise ValueError("NodeType should be chosen from 'Work' and 'PS'")
        if self.cmd_params["TrainModeId"] == "" or type(self.cmd_params["TrainModeId"]) != int:
            raise ValueError("TrainModeId should be <int> and should not be nil")
