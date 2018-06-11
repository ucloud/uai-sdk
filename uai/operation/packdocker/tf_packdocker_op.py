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

from uai.operation.tar.tf_tar_op import UaiServiceTFTarOp
from uai.operation.packdocker.base_packdocker_op import UaiServiceDockerPackOp

class UaiServiceTFDockerPackOp(UaiServiceDockerPackOp, UaiServiceTFTarOp):
    """
    TF Docker Image Pack Tool Class
    """
    def __init__(self, parser):
        super(UaiServiceTFDockerPackOp, self).__init__(parser)
        self.platform = 'tensorflow'


    def _add_args(self):
        super(UaiServiceTFDockerPackOp, self)._add_args()

    def _parse_args(self, args):
        super(UaiServiceTFDockerPackOp, self)._parse_args(args)
        self._parse_model_args(args)