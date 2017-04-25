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

from .base_conf import ArchJsonConf, ArchJsonConfLoader


class KerasJsonConf(ArchJsonConf):
    """Keras Json Config class

    """

    def __init__(self, parser):
        """ Keras Json Config Class, Use the super to init
        """
        super(KerasJsonConf, self).__init__('keras', parser)

    def _add_args(self):
        super(KerasJsonConf, self)._add_args()

        self.args_parser.add_argument(
            '--model_name',
            type=str,
            required=True,
            help='the Keras model name')
        self.args_parser.add_argument(
            '--all_one_file',
            type=bool,
            required=True,
            help='whether the model is all in one file')
        self.args_parser.add_argument(
            '--model_arc_type',
            type=str,
            default='json',
            help='the model arc type to save')
        self.params = vars(self.parser.parse_args())

    def _load_conf_params(self):
        """ Config the conf_params from the CMD
        """
        super(KerasJsonConf, self)._load_conf_params()
        self.conf_params['http_server'] = {
            'exec': {
                'main_file': self.params['main_file'],
                'main_class': self.params['main_class']
            },
            'keras': {
                'model_dir': self.params['model_dir'],
                'model_name': self.params['model_name'],
                'all_one_file': self.params['all_one_file'],
                'model_arc_type': self.params['model_arc_type'],
            }
        }

    def get_conf_params(self):
        return self.conf_params

    def get_arg_params(self):
        return self.params


class KerasJsonConfLoader(ArchJsonConfLoader):
    def __init__(self, conf):
        super(KerasJsonConfLoader, self).__init__(conf)

    def _load(self):
        super(KerasJsonConfLoader, self)._load()
        self.model_dir = self.server_conf['keras']['model_dir']
        self.model_name = self.server_conf['keras']['model_name']
        self.all_one_file = self.server_conf['keras']['all_one_file']
        self.model_arc_type = self.server_conf['keras']['model_arc_type']

    def get_model_dir(self):
        return self.model_dir

    def get_model_name(self):
        return self.model_name

    def get_all_one_file(self):
        return self.all_one_file

    def get_model_arc_type(self):
        return self.model_arc_type
