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


class CheckAndGetUAITrainBaseImageApiOp(BaseUAITrainAPIOp):
    """
    CheckAndGetUAITrainBaseImageAPI

        Identical with UAI Train CheckUAITrainBaseImgExists API func
        Input:
            OSVersion           int(required)       OS version
            PythonVersion       int(required)       Python version
            AIFrameVersion      int(required)       AI Framework and version
            AcceleratorId       int(required)       Acc device type
        Output:
            TotalCount      string(not required)         Image count
            BimgName        string array(not required)   Image names
            BimgPullCmd     string array(not required)   Image pull cmds
    """
    ACTION_NAME = "CheckUAITrainBaseImgExists"
    def __init__(self, pub_key, priv_key, os_v, py_v, ai_frame_v, acc_id, project_id="", region="", zone=""):
        super(CheckAndGetUAITrainBaseImageApiOp, self).__init__(self.ACTION_NAME, pub_key, priv_key, project_id, region, zone)
        self.cmd_params[PARAM_OS_VERSION] = os_v
        self.cmd_params[PARAM_PYTHON_VERSION] = py_v
        self.cmd_params[PARAM_AI_FRAME_VERSION] = ai_frame_v
        self.cmd_params[PARAM_ACC_ID] = acc_id
    
    def _check_args(self):
        super(CheckAndGetUAITrainBaseImageApiOp, self)._check_args()

        if self.cmd_params[PARAM_OS_VERSION] == "" or type(self.cmd_params[PARAM_OS_VERSION]) != int:
            raise ValueError("{0} should be <int> and should not be nil".format(PARAM_OS_VERSION))

        if self.cmd_params[PARAM_PYTHON_VERSION] == "" or type(self.cmd_params[PARAM_PYTHON_VERSION]) != int:
            raise ValueError("{0} should be <int> and should not be nil".format(PARAM_PYTHON_VERSION))

        if self.cmd_params[PARAM_AI_FRAME_VERSION] == "" or type(self.cmd_params[PARAM_AI_FRAME_VERSION]) != int:
            raise ValueError("{0} should be <int> and not nil".format(PARAM_AI_FRAME_VERSION))

        if self.cmd_params[PARAM_ACC_ID] == "" or type(self.cmd_params[PARAM_ACC_ID]) != int:
            raise ValueError("{0} should be <int> and should not be nil".format(PARAM_ACC_ID))
