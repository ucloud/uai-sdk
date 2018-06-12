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

from uai.arch_conf.base_conf import ArchJsonConf
from uai.arch_conf.base_conf import ArchJsonConfLoader

class XGBoostJsonConf(ArchJsonConf):
    """ XGBoost Json Config class
    """
    def __init__(self, parser):
        """ XGBoost Json Config Class, Use the super to init
        """
        super(XGBoostJsonConf, self).__init__('xgboost', parser)

    def _add_args(self):
        super(XGBoostJsonConf, self)._add_args()

    def load_params(self):
        super(XGBoostJsonConf, self).load_params()

    def _load_conf_params(self):
        """ Config the conf_params from the CMD
        """
        super(XGBoostJsonConf, self)._load_conf_params()
        self.conf_params['http_server'] = {
            'exec': {
                'main_file': self.params['main_file'],
                'main_class': self.params['main_class']
            },
            'xgboost': {
                'model_name': self.params['model_name']                
            }
        }

    def _load_args(self):
        super(XGBoostJsonConf, self)._load_args()

    def get_conf_params(self):
        self._load_args()
        return self.conf_params

    def get_arg_params(self):
        return self.params

class XGBoostJsonConfLoader(ArchJsonConfLoader):
    def __init__(self, conf):
        super(XGBoostJsonConfLoader, self).__init__(conf)

    def _load(self):
        super(XGBoostJsonConfLoader, self)._load()
        self.model_name = self.server_conf['xgboost']['model_name']
    
    def get_model_name(self):
        return self.model_name
