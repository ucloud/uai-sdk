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
        if len(parser._actions) == 1:
            self._add_args()
        #self._load_args()

    def _add_args(self):
        """ Add common args here
            Child class can add its own args in _add_args
        """
        subparsers = self.parser.add_subparsers(dest='commands', help='commands')

        # A pack command
        pack_parser = subparsers.add_parser('pack', help='Pack local code into docker and upload to uhub')
        self._add_account_args(pack_parser)
        self._add_pack_args(pack_parser)

        # A update command
        create_parser = subparsers.add_parser('create', help='Create uai train job')
        self._add_account_args(create_parser)
        self._add_create_args(create_parser)

    def load_params(self):
        self.params = vars(self.parser.parse_args())


        #set default / solid params
        # if not self.params["accelerator"]:
        #     self.params["accelerator"] = "gpu"

    def _add_account_args(self, parser):
        args_parser = parser.add_argument_group(
                         'User-Params', 'User Authentication Parameters')
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
            '--project_id',
            type=str,
            required=False,
            help='the project id of ucloud, could be null')

    def _add_create_args(self, parser):
        args_parser = parser.add_argument_group(
            'Uai-Params', 'Uai TrainJob Managment Parameters')
        args_parser.add_argument(
            '--job_name',
            type=str,
            required=True,
            help='the uai job name')
        args_parser.add_argument(
            '--worker_id',
            type=int,
            default=1860001,
            help='the type of worker server')
        args_parser.add_argument(
            '--uhub_path',
            type=str,
            required=True,
            help='uhubpath')
        args_parser.add_argument(
            '--ufile_datapath',
            type = str,
            required = True,
            help = 'ufile_datapath')
        args_parser.add_argument(
            '--ufile_outputpath',
            type = str,
            required = True,
            help = 'ufile_outputpath')
        args_parser.add_argument(
            '--docker_cmd',
            type = str,
            required = True,
            help = 'docker_cmd')
        args_parser.add_argument(
            '--max_exectime',
            type = int,
            default = 6,
            help = 'max execute time')

    def _add_pack_args(self, parser):
        code_parse = parser.add_argument_group(
            'Code-Params', 'Code Parameters, help to pack user code into docker image')
        code_parse.add_argument(
            '--code_path',
            type=str,
            required=True,
            help='the path of the user program containing all code files')
        code_parse.add_argument(
            '--mainfile_path',
            type=str,
            required=True,
            help='the related path of main python file considering code_path as root')
        #todo: add cmd line parameters outside baseconfig, according to different aiframe
        self.pack_parser = code_parse

        uhub_parse = parser.add_argument_group(
            'Docker-Params', 'Docker Parameters, help to upload docker image automatically')
        uhub_parse.add_argument(
            '--uhub_username',
            type=str,
            required=True,
            help='username to login uhub, which is also username to ucloud console')
        uhub_parse.add_argument(
            '--uhub_password',
            type=str,
            required=True,
            help='password to login uhub, which is also password to ucloud console')
        uhub_parse.add_argument(
            '--uhub_registry',
            type=str,
            required=True,
            help='the name of registry owned by user on ucloud console')
        uhub_parse.add_argument(
            '--uhub_imagename',
            type=str,
            required=True,
            help='the name of user docker image')
        uhub_parse.add_argument(
            '--uhub_imagetag',
            type=str,
            required=False,
            help='the tag of user docker image')

        container_parse = parser.add_argument_group(
            'Container-Params', 'Container Enviroment Parameters')
        container_parse.add_argument(
            '--os',
            type=str,
            default='ubuntu',
            help='the type of the docker os')
        container_parse.add_argument(
            '--language',
            type=str,
            default='python-2.7.6',
            help='the language of the docker')
        container_parse.add_argument(
            '--ai_arch_v',
            type=str,
            # default='tensorflow-1.1.0',
            required=True,
            help='AI architecture and specific version')
        container_parse.add_argument(
            '--accelerator',
            type=str,
            default='gpu',
            help='AI architecture and specific version')

        cmd_gen_parse = parser.add_argument_group(
            'Cmd-Gen-Params', 'Cmd generate params')
        cmd_gen_parse.add_argument(
            '--test_data_path',
            type=str,
            required=True,
            help='the data dir for local test')
        cmd_gen_parse.add_argument(
            '--test_output_path',
            type=str,
            required=True,
            help='the output dir for local test')
        cmd_gen_parse.add_argument(
            '--train_params',
            type=str,
            required=True,
            help='the train related params')


    def _load_conf_params(self):
        pass

    def _load_args(self):
        """ Json param loader
        """
        self._load_conf_params()
