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
from uai.arch.base_model import AiUcloudModel
from uai.arch_conf.tf_conf import TFJsonConf, TFJsonConfLoader

class TFAiUcloudModel(AiUcloudModel):
    """Base model class for user defined Tensorflow Model
    """

    def __init__(self, conf=None, model_type='tensorflow'):
        super(TFAiUcloudModel, self).__init__(conf, model_type)
        self.output = {}
        self._parse_conf(conf)
        self.model = self.load_model()

    def _parse_conf(self, conf):
        """
        Parse Tensorflow related config
        Args:
            conf:    key/val object for AI architecture specific config
        """
        tf_json_conf_loader = TFJsonConfLoader(conf)
        self.model_dir = tf_json_conf_loader.get_model_dir()

    def load_model(self):
        pass

    def execute(self, data, batch_size):
        pass
