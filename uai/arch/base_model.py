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
from uai.arch_conf.base_conf import ArchJsonConf, ArchJsonConfLoader


class AiUcloudModel(object):
    """
    Base class struct for user defined AI Model
    """

    def __init__(self, conf, model_type):
        """
        Args:
            conf:       key/val object for AI architecture specific config
            model_type: str, the model type
        """
        self.conf = conf
        self.model_type = model_type
        self._parse_conf(conf)

    def _parse_conf(self, conf):
        arch_json_conf_loader = ArchJsonConfLoader(conf)
        self.main_file = arch_json_conf_loader.get_main_file
        self.main_class = arch_json_conf_loader.get_main_class

    def load_model(self):
        pass

    def execute(self, data, batch_size):
        pass
