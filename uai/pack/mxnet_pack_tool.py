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
from uai.arch_conf.mxnet_conf import MXNetJsonConf
from uai.arch_conf.mxnet_conf import MXNetJsonConfLoader

class MXNetPackTool(UaiPackTool):
    """ MXNet Pack Tool class
    """
    def __init__(self, parser):
        super(MXNetPackTool, self).__init__('mxnet', parser)

    def _add_args(self):
        """ MXNet specific _add_args tool to parse MXNet params
        """
        self.config = MXNetJsonConf(self.parser)


    def _load_args(self):
        self.config.load_params()
        self.conf_params = self.config.get_conf_params()
        self.params = self.config.get_arg_params()

        conf_loader = MXNetJsonConfLoader(self.conf_params)
        self.model_dir = conf_loader.get_model_dir()
        self.num_epoch = conf_loader.get_num_epoch()
        self.model_prefix = conf_loader.get_model_prefix()
        return

    def _get_model_list(self):
        """ MXNet specific _get_model_list tool to get model filelist
        """
        self.model_arch_file = self.model_prefix + '-' + 'symbol'+ '.json'
        num_epoch = str(self.num_epoch).zfill(4)
        self.model_weight_file = self.model_prefix + '-' + num_epoch + '.params'
        self.filelist.append(self.model_arch_file)
        self.filelist.append(self.model_weight_file)