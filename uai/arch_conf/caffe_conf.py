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

class CaffeJsonConf(ArchJsonConf):
    """ Caffe Json Config class
    """
    def __init__(self, parser):
        """ Caffe Json Config Class, Use the super to init
        """
        super(CaffeJsonConf, self).__init__('caffe', parser)

    def _add_args(self):
        super(CaffeJsonConf, self)._add_args()

        #add pack parameters
        # self.pack_parser.add_argument(
        #     '--ai_arch_v',
        #     type=str,
        #     default='caffe-1.0.0',
        #     help='ai arch version of caffe')
        self.pack_parser.add_argument(
            '--model_name',
            type=str,
            required=True,
            help='the Caffe model name')

        # add deploy parameters
        # self.deploy_parser.add_argument(
        #     '--ai_arch_v',
        #     type=str,
        #     default='caffe-1.0.0',
        #     help='ai arch version of caffe')
        # self.deploy_parser.add_argument(
        #     '--model_name',
        #     type=str,
        #     required=False,
        #     help='the Caffe model name')
        # self.params = vars(self.parser.parse_args())


    def _load_conf_params(self):
        """ Config the conf_params from the CMD
        """
        super(CaffeJsonConf, self)._load_conf_params()
        self.conf_params['http_server'] = {
            'exec': {
                'main_file': self.params['main_file'],
                'main_class': self.params['main_class']
            },
            'caffe': {
                'model_dir': self.params['model_dir'],
                'model_name': self.params['model_name']
            }
        }

    def _load_args(self):
        super(CaffeJsonConf, self)._load_args()

    def get_conf_params(self):
        self._load_args()
        return self.conf_params

    def get_arg_params(self):
        return self.params


class CaffeJsonConfLoader(ArchJsonConfLoader):
    def __init__(self, conf):
        super(CaffeJsonConfLoader, self).__init__(conf)

    def _load(self):
        super(CaffeJsonConfLoader, self)._load()
        self.model_dir = self.server_conf['caffe']['model_dir']
        self.model_name = self.server_conf['caffe']['model_name']

    def get_model_dir(self):
        return self.model_dir

    def get_model_name(self):
        return self.model_name