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

import os
from uai.operation.tar.base_tar_op import UaiServiceTarOp

class UaiServiceTFTarOp(UaiServiceTarOp):
    """ TensorFlow Tar Class
    """
    def __init__(self, parser):
        super(UaiServiceTFTarOp, self).__init__(parser)

    def _add_args(self):
        super(UaiServiceTFTarOp, self)._add_args()

    def _parse_model_args(self, args):
        self.conf_params['http_server'] = {
            'exec': {
                'main_file': self.main_file,
                'main_class': self.main_class
            },
            'tensorflow': {
                'model_dir': self.model_dir,
            }
        }

    def _parse_args(self, args):
        super(UaiServiceTFTarOp, self)._parse_args(args)
        self._parse_model_args(args)

    def _get_model_list(self):
        model_filelist = os.listdir(os.path.join(self.pack_file_path, self.model_dir))
        for i in model_filelist:
            model_file = os.path.join(self.model_dir, i)
            self.filelist.append(model_file)
