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
from uai.arch.base_model import AiUcloudModel
from uai.arch_conf.keras_conf import KerasJsonConf, KerasJsonConfLoader


class KerasAiUcloudModel(AiUcloudModel):
    """
    Base model class for user defined Keras Model
    """

    def __init__(self, conf=None, model_type='keras'):
        super(KerasAiUcloudModel, self).__init__(conf, model_type)
        self.output = {}
        self._parse_conf(conf)
        self.model = self.load_model()

    def _parse_conf(self, conf):
        """
        Parse Keras related config
        Args:
            conf:    key/val object for AI architecture specific config
        """
        keras_json_conf_loader = KerasJsonConfLoader(conf)
        self.model_dir = keras_json_conf_loader.get_model_dir()
        self.model_name = keras_json_conf_loader.get_model_name()
        self.all_one_file = keras_json_conf_loader.get_all_one_file()
        if not self.all_one_file:
            self.model_arc_type = keras_json_conf_loader.get_model_arc_type()
            self.model_arc_file = os.path.join(
                self.model_dir, self.model_name + '.' + self.model_arc_type)
            self.model_weight_file = os.path.join(self.model_dir,
                                                  self.model_name + '.h5')
        else:
            # when all_one_file true 
            self.model_file = os.path.join(self.model_dir,
                                           self.model_name + '.h5')

    def load_model(self):
        pass

    def execute(self, data, batch_size):
        pass
