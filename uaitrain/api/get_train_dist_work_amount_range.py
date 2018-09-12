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


class GetUAITrainDistributeWorkAmountRangeApiOp(BaseUAITrainAPIOp):
    """
    GetUAITrainDistributeWorkAmountRangeAPI

        Identical with UAI Train GetUAITrainDistributeWorkAmountRange API func
        Output:
            RetCode            int                      API return code: 0: success, others: error code
            Action             string                   Action name
            Message            string                   Message: error description
            SetName            string                   current set name
            Min                int                      minimum dist work amount when using dist-training
            Max                int                      maximum dist work amount when using dist-training
    """
    ACTION_NAME = "GetUAITrainDistributeWorkAmountRange"

    def __init__(self, pub_key, priv_key, project_id="", region="", zone=""):
        super(GetUAITrainDistributeWorkAmountRangeApiOp, self).__init__(self.ACTION_NAME, pub_key, priv_key, project_id, region, zone)

    def _check_args(self):
        super(GetUAITrainDistributeWorkAmountRangeApiOp, self)._check_args()
