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
from uai.arch_conf.keras_conf import KerasJsonConf
from uai.arch_conf.keras_conf import KerasJsonConfLoader

class KerasPackTool(UaiPackTool):
    """ Keras Pack Tool class
    """
    def __init__(self, parser):
        super(KerasPackTool, self).__init__('keras', parser)

    def _add_args(self):
        """ Keras specific _add_args tool to parse Keras params
        """
        self.config = KerasJsonConf(self.parser)

    def _load_args(self):
        self.config.load_params()
        self.conf_params = self.config.get_conf_params()
        self.params = self.config.get_arg_params()

        conf_loader = KerasJsonConfLoader(self.conf_params)
        self.model_dir = conf_loader.get_model_dir()
        self.model_name = conf_loader.get_model_name()
        self.all_one_file = conf_loader.get_all_one_file()
        self.model_arch_type = conf_loader.get_model_arch_type()
        return


    def _get_model_list(self):
        """ Keras specific _get_model_list tool to get model filelist
        """
        if not self.all_one_file:
            self.model_arch_file = os.path.join(self.model_dir,
                                               self.model_name + '.' + self.model_arch_type)
            self.model_weight_file = os.path.join(self.model_dir, self.model_name + '.h5')
            self.filelist.append(self.model_arch_file)
            self.filelist.append(self.model_weight_file)
        else:
            self.model_file = os.path.join(self.model_dir, self.model_name + '.h5')
            self.filelist.append(self.model_file)