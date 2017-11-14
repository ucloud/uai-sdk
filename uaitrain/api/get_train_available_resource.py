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

class GetUAITrainAvailableResourceOp(BaseUAITrainAPIOp):
    ACTION_NAME = "GetUAITrainAvailableResource"
    """
    GetUAITrainAvailableResourceOp
        Compatable with UAI Train GetUAITrainAvailableResource API func
        Input:
            pub_key             string(required) Public key of the user
            priv_key            string(required) Private key of the user
            project_id          int(optional)    Project ID of the job
            region              string(optional) Which Region to run the job
            zone                string(optional) Which Zone in the Region to run the job
            node_type           string(optional) the type of node, default is 'Work'. 
                                                    'Work': train node
                                                    'PS': param node
        Output:
            RetCode         int(required)                Op return code: 0: success, others: error code
            TotalCount      string(required)             the count of result
            Message         string(not required)         Message: error description
            DataSet         []                           the detailed information of resource
    """

    def __init__(self, pub_key, priv_key, node_type='Work', project_id="", region="", zone=""):
        super(GetUAITrainAvailableResourceOp, self).__init__(self.ACTION_NAME,
                                                     pub_key,
                                                     priv_key,
                                                     project_id,
                                                     region,
                                                     zone)
        self.cmd_params["NodeType"] = node_type

    def _check_args(self):
        super(GetUAITrainAvailableResourceOp, self)._check_args()