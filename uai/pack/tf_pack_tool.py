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
from base_pack_tool import UaiPackTool
from uai.arch_conf.tf_conf import TFJsonConf
from uai.arch_conf.tf_conf import TFJsonConfLoader

class TFPackTool(UaiPackTool):
    """ TensorFlow Pack Tool class
    """
    def __init__(self, parser):
        super(TFPackTool, self).__init__('tensorflow', parser)

    def _add_args(self):
        """ TensorFlow specific _add_args tool to parse TensorFlow params
        """
        self.config = TFJsonConf(self.parser)


    def _load_args(self):
        self.conf_params = self.config.get_conf_params()
        self.params = self.config.get_arg_params()

        conf_loader = TFJsonConfLoader(self.conf_params)
        self.model_dir = conf_loader.get_model_dir()
        return

    def _get_model_list(self):
        """ TensorFlow specific _get_model_list tool to get model filelist
        """
        model_filelist = os.listdir(os.path.join(self.params['pack_file_path'], self.params['model_dir']))
        for i in model_filelist:
            model_file = os.path.join(self.params['model_dir'], i)
            self.filelist.append(model_file)