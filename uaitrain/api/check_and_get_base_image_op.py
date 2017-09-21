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

CHECK_AND_GET_UAI_TRAIN_BASE_IMAGE_ACTION = 'CheckUAITrainBaseImgExists'
PARAM_OS_VERSION = 'OSVersion'
PARAM_PYTHON_VERSION = 'PythonVersion'
PARAM_AI_FRAME_VERSION = 'AIFrameVersion'
PARAM_ACC_ID = 'AcceleratorID'

class CheckAndGetUAITrainBasesImageAPIOp(BaseUAITrainAPIOp):
    """
    CheckAndGetUAITrainBasesImageAPIOp
        Compatable with UAI Train CheckUAITrainBaseImgExists API func
        Input:
			PublicKey       string(required) Public key of the user
            ProjectId       int(optional)    Project ID of the task
            Region          string(optional) Which Region to run the task
            Zone            string(optional) Which Zone in the Region to run the task
            OSVersion       int(required)    OS version
            PythonVersion   int(required)    Python version
            AIFrameVersion  int(required)    AI Framework and version
            AcceleratorId   int(required)    Acc device type

        Output:
            RetCode       int(required)                Op return code: 0: success, others: error code
            Action        string(required)             Action name
            Message       string(not required)         Message: error description
            TotalCount    string(not required)         Image count
            BimgName      string array(not required)   Image names
            BimgPullCmd   string array(not required)   Image pull cmds
    """
    def __init__(self, pub_key, priv_key, os_v, py_v, ai_frame_v, acc_id, project_id="", region="", zone=""):
        super(CheckAndGetUAITrainBasesImageAPIOp, self).__init__(CHECK_AND_GET_UAI_TRAIN_BASE_IMAGE_ACTION, 
            pub_key, 
            priv_key, 
            project_id,
            region,
            zone)
        self.cmd_params[PARAM_OS_VERSION] = os_v
        self.cmd_params[PARAM_PYTHON_VERSION] = py_v
        self.cmd_params[PARAM_AI_FRAME_VERSION] = ai_frame_v
        self.cmd_params[PARAM_ACC_ID] = acc_id
    
    def _check_args(self):
        super(CheckAndGetUAITrainBasesImageAPIOp, self)._check_args()

        if type(self.cmd_params[PARAM_OS_VERSION]) != int:
            raise RuntimeError("{0} should be <int>".format(PARAM_OS_VERSION))

        if type(self.cmd_params[PARAM_PYTHON_VERSION]) != int:
            raise RuntimeError("{0} should be <int>".format(PARAM_PYTHON_VERSION))

        if type(self.cmd_params[PARAM_AI_FRAME_VERSION]) != int:
            raise RuntimeError("{0} should be <int>".format(PARAM_AI_FRAME_VERSION))

        if type(self.cmd_params[PARAM_ACC_ID]) != int:
            raise RuntimeError("{0} should be <int>".format(PARAM_ACC_ID))
