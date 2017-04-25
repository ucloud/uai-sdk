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


class ArchJsonConf(object):
    """ The Base Json Config Class with UAI
    """

    def __init__(self, platform, parser):
        self.platform = platform
        self.parser = parser
        self.conf_params = {}
        self._add_args()
        self._load_args()

    def _add_args(self):
        """ Add common args here
            Child class can add its own args in _add_args
        """
        args_parser = self.parser.add_argument_group(
            'Docker-Params', 'Docker related conf args')
        args_parser.add_argument(
            '--bucket',
            type=str,
            required=True,
            help='the name of ufile bucket')
        args_parser.add_argument(
            '--public_key',
            type=str,
            required=True,
            help='the public key of the user')
        args_parser.add_argument(
            '--private_key',
            type=str,
            required=True,
            help='the private key of the user')
        args_parser.add_argument(
            '--os',
            type=str,
            default='ubuntu',
            help='the type of the docker os')
        args_parser.add_argument(
            '--language',
            type=str,
            default='python-2.7',
            help='the language of the docker')
        args_parser.add_argument(
            '--os_deps', type=str, help='the dependency of the ubuntu apt-get')
        args_parser.add_argument(
            '--pip', type=str, help='the dependency of the python pip')
        args_parser = self.parser.add_argument_group(
            'HttpServer-Params', 'httpserver related conf args')
        args_parser.add_argument(
            '--main_file',
            type=str,
            required=True,
            help='the main file of the user program')
        args_parser.add_argument(
            '--main_class',
            type=str,
            required=True,
            help='the main class name of the user program')
        args_parser.add_argument(
            '--model_dir',
            type=str,
            required=True,
            help='the tensorflow model dir')
        args_parser.add_argument(
            '--code_files',
            type=str,
            required=True,
            help='the all python files')
        args_parser = self.parser.add_argument_group('Other-Params',
                                                     'other conf args')
        args_parser.add_argument(
            '--request_url', type=str, required=True, help='the request url ')
        args_parser.add_argument(
            '--max_poll_steps',
            type=int,
            default=120,
            help='the default steps (10min == 120) to poll the state of deploy')
        self.args_parser = args_parser

    def _load_conf_params(self):
        """ Config the conf_params from the CMD
            common conf params here
            Child class can add its specific params on its own _load_conf_params
        """
        self.conf_params = {
            'docker': {
                'ufile': {
                    'code_files': [
                        code_file.strip()
                        for code_file in self.params['code_files'].split(',')
                    ],
                    'model_dir': self.params['model_dir'],
                    'bucket': self.params['bucket'],
                    'public_key': self.params['public_key'],
                    'private_key': self.params['private_key']
                },
                'dockerfile': {
                    'driver': self.platform,
                    'language': {
                        'version': self.params['language'].split('-')[1],
                        'type': self.params['language'].split('-')[0]
                    },
                    'os': self.params['os'],
                    'os-deps':
                    [dep.strip() for dep in self.params['os_deps'].split(',')],
                    'pip':
                    [pip_dep.strip() for pip_dep in self.params['pip'].split(',')]
                }
            }
        }

    def _load_args(self):
        """ Json param loader
        """
        self._load_conf_params()

    def get_params(self):
        """ The Common method to get the parms of the specificed platform
        """
        self.params[self.platform] = self.conf_params
        return self.params

class ArchJsonConfLoader(object):
    def __init__(self, conf):
        self.conf = conf
        self._load()

    def _load(self):
        self.server_conf = self.conf['http_server']
        self.main_file = self.server_conf['exec']['main_file']
        self.main_class = self.server_conf['exec']['main_class']

    def get_main_file(self):
        return self.main_file

    def get_main_class(self):
        return self.main_class

class DeleteConf(object):
    """ The Base Delete Config Class with UAI
    """

    def __init__(self, parser):
        self.params = {}
        self.conf_params = {}
        self.parser = parser
        self.add_args()
        self.load_args()

    def add_args(self):
        args_parser = self.parser.add_argument_group(
            'Delete-Params', 'Delete related conf args')
        args_parser.add_argument(
            '--public_key',
            type=str,
            required=True,
            help='the public key of the user')
        args_parser.add_argument(
            '--private_key',
            type=str,
            required=True,
            help='the private key of the user')
        args_parser.add_argument(
            '--task_id',
            type=str,
            required=True,
            help='the uai service task id')
        self.args_parser = args_parser
        
    def _load_conf_params(self):
        self.conf_params = {
            'public_key': self.params['public_key'],
            'private_key': self.params['private_key'],
            'task_id': self.params['task_id'],
        }

    def load_args(self):
        self.params = vars(self.parser.parse_args())
        print self.params

        self._load_conf_params()
