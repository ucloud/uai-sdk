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

GET_UAI_TRAIN_ENV_PKG_ACTION = 'GetUAITrainEnvPkg'
PARAM_PKG_TYPE = 'PkgType'

class GetUAITrainEnvPkgAPIOp(BaseUAITrainAPIOp):
    """
    GetUAITrainEnvPkgAPIOp
        Compatable with UAI Train CheckUAITrainBaseImgExists API func
        Input:
			PublicKey       string(required) Public key of the user
            ProjectId       int(optional)    Project ID of the task
            Region          string(optional) Which Region to run the task
            Zone            string(optional) Which Zone in the Region to run the task
            PkgType         string(required) Package Type to check including OS, Python, AIFrame, Accelerator

        Output:
            RetCode       int(required)                Op return code: 0: success, others: error code
            Action        string(required)             Action name
            Message       string(not required)         Message: error description
            
    """
    def __init__(self, pub_key, priv_key, pkg_type, project_id="", region="", zone=""):
        super(GetUAITrainEnvPkgAPIOp, self).__init__(GET_UAI_TRAIN_ENV_PKG_ACTION, 
            pub_key, 
            priv_key, 
            project_id,
            region,
            zone)
        self.cmd_params[PARAM_PKG_TYPE] = pkg_type
    
    def _check_args(self):
        super(GetUAITrainEnvPkgAPIOp, self)._check_args()
        
        if self.cmd_params[PARAM_PKG_TYPE] == "":
            raise RuntimeError("You should specify a pkg_type to search: OS, Python, AIFrame, Accelerator")
