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

PARAM_PKG_TYPE = 'PkgType'


class GetUAITrainEnvPkgAPIOp(BaseUAITrainAPIOp):
    """
    GetUAITrainEnvPkgAPI

        Identical with UAI Train GetUAITrainEnvPkg API func
        Input:
            PkgType             string(required)       Package Type to check including OS, Python, AIFrame, Accelerator
        Output:
            RetCode             int                    API return code: 0: success, others: error code
            Action              string                 Action name
            Message             string                 Message: error description
            TotalCount          int                    Available pkg count
            DataSet             Array                  []PkgInfo

        PkgInfo:
            PkgId               int64                  Id of current package
            PkgName             string                 Name of current package
            PkgVersion          string                 Version of current package
            PkgType             string                 Type of current package
    """
    ACTION_NAME = "GetUAITrainEnvPkg"

    def __init__(self, pub_key, priv_key, pkg_type, project_id="", region="", zone=""):
        super(GetUAITrainEnvPkgAPIOp, self).__init__(self.ACTION_NAME, pub_key, priv_key, project_id, region, zone)
        self.cmd_params[PARAM_PKG_TYPE] = pkg_type
    
    def _check_args(self):
        super(GetUAITrainEnvPkgAPIOp, self)._check_args()
        
        if self.cmd_params[PARAM_PKG_TYPE] == "" or type(self.cmd_params[PARAM_PKG_TYPE]) != str:
            raise ValueError("{0} should be <str> and should not be nil".format(PARAM_PKG_TYPE))
