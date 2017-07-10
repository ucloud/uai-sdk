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
from uai.arch_conf.caffe_conf import CaffeJsonConf
from uai.arch_conf.caffe_conf import CaffeJsonConfLoader

class CaffeAiUcloudModel(AiUcloudModel):
    """
        Base model class for user defined Caffe Model
    """
    def __init__(self, conf=None, model_type='caffe'):
        super(CaffeAiUcloudModel, self).__init__(conf, model_type)
        self.output = {}
        self._parse_conf(conf)
        self.load_model()

    def _parse_conf(self, conf):
        """
            Parse Caffe related config
            Args:
                conf: key/val object for AI architecture specific config
        """
        caffe_json_conf_loader = CaffeJsonConfLoader(conf)
        self.model_dir = caffe_json_conf_loader.get_model_dir()
        self.model_name = caffe_json_conf_loader.get_model_name()
        self.model_arch_file = str(os.path.join(self.model_dir, self.model_name + '.prototxt'))
        self.model_weight_file = str(os.path.join(self.model_dir, self.model_name + '.caffemodel'))
        
    def load_model(self):
        pass

    def execute(self, data, batch_size):
        pass
