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
from uai.arch_conf.base_conf import ArchJsonConf
from uai.arch_conf.base_conf import ArchJsonConfLoader

class MXNetJsonConf(ArchJsonConf):
    """ MXNet Json Config class
    """
    def __init__(self, parser):
        """ MXNet Json Config Class, Use the super to init
        """
        super(MXNetJsonConf, self).__init__('mxnet', parser)

    def _add_args(self):
        super(MXNetJsonConf, self)._add_args()

        # #add pack parameters
        # self.pack_parser.add_argument(
        #     '--ai_arch_v',
        #     type=str,
        #     default='mxnet-0.9.5',
        #     help='ai arch version of mxnet')
        self.pack_parser.add_argument(
            '--model_name',
            type=str,
            required=True,
            help='the MXNet model name')
        self.pack_parser.add_argument(
            '--num_epoch',
            type=int,
            required=True,
            help='the num of the model ckpt epoch')

        # #add deploy parameters
        # self.deploy_parser.add_argument(
        #     '--ai_arch_v',
        #     type=str,
        #     default='mxnet-0.9.5',
        #     help='ai arch version of mxnet')
        # self.deploy_parser.add_argument(
        #     '--model_name',
        #     type=str,
        #     required=False,
        #     help='the MXNet model name')
        # self.deploy_parser.add_argument(
        #     '--num_epoch',
        #     type=int,
        #     required=False,
        #     help='the num of the model ckpt epoch')

        # self.params = vars(self.parser.parse_args())

    def load_params(self):
        super(MXNetJsonConf, self).load_params()

    def _load_conf_params(self):
        """ Config the conf_params from the CMD
        """
        super(MXNetJsonConf, self)._load_conf_params()
        self.conf_params['http_server'] = {
            'exec': {
                'main_file': self.params['main_file'],
                'main_class': self.params['main_class']
            },
            'mxnet': {
                'model_dir': self.params['model_dir'],
                'model_name': self.params['model_name'],
                'num_epoch': self.params['num_epoch'],
            }
        }

    def _load_args(self):
        """ MXNet Json Load Method
        """
        super(MXNetJsonConf, self)._load_args()

    def get_conf_params(self):
        self._load_args()
        return self.conf_params

    def get_arg_params(self):
        return self.params


class MXNetJsonConfLoader(ArchJsonConfLoader):
    def __init__(self, conf):
        super(MXNetJsonConfLoader, self).__init__(conf)

    def _load(self):
        super(MXNetJsonConfLoader, self)._load()
        self.model_dir = self.server_conf['mxnet']['model_dir']
        self.model_name = self.server_conf['mxnet']['model_name']
        self.num_epoch = self.server_conf['mxnet']['num_epoch']
        self.model_prefix = os.path.join(self.model_dir, self.model_name)

    def get_model_dir(self):
        return self.model_dir

    def get_model_name(self):
        return self.model_name

    def get_num_epoch(self):
        return self.num_epoch

    def get_model_prefix(self):
        return self.model_prefix
