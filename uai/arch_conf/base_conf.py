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

        # A create command
        create_parser = subparsers.add_parser('create', help='Create new uai-service')
        self._add_account_args(create_parser)
        self._add_create_args(create_parser)

        # A pack command
        pack_parser = subparsers.add_parser('pack', help='Pack local code into tar file')
        self._add_account_args(pack_parser)
        self._add_pack_args(pack_parser)

        # A deploy command
        deploy_parser = subparsers.add_parser('deploy', help='Deploy version for certain serivce id')
        self._add_account_args(deploy_parser)
        self._add_deploy_args(deploy_parser)
     
        # A checkprogress command
        checkprogress_parser = subparsers.add_parser('checkprogress', help='Check version deploying status for certain serivce version')
        self._add_account_args(checkprogress_parser)
        self._add_checkprogress_args(checkprogress_parser)

        # A delete command
        delete_parser = subparsers.add_parser('delete', help='Remove a whole service or a version in a certian service')
        self._add_account_args(delete_parser)
        self._add_delete_args(delete_parser)
        
        # A stop command
        stop_parser = subparsers.add_parser('stop', help='Stop a whole service or a version in a certian service')
        self._add_account_args(stop_parser)
        self._add_stop_args(stop_parser)
        
        # A start command
        start_parser = subparsers.add_parser('start', help='Start a version in a certian service')
        self._add_account_args(start_parser)
        self._add_start_args(start_parser)

        # A list service command
        listservice_parser = subparsers.add_parser('listservice', help='List serivces info, could specify one by service_id')
        self._add_account_args(listservice_parser)
        self._add_listservice_args(listservice_parser)

        # A list version command
        listversion_parser = subparsers.add_parser('listversion', help='List versions info of a specified uai service, could specify a certain version by service_version')
        self._add_account_args(listversion_parser)
        self._add_listversion_args(listversion_parser)

        # A modify service name command
        modifyname_parser = subparsers.add_parser('modifyname', help='Modify service name')
        self._add_account_args(modifyname_parser)
        self._add_modifyname_args(modifyname_parser)
        
        # A modify service name command
        modifyweight_parser = subparsers.add_parser('modifyweight', help='Modify service weight for grayscale publishing')
        self._add_account_args(modifyweight_parser)
        self._add_modifyweight_args(modifyweight_parser)

        # A get available env command
        availableenv_parser = subparsers.add_parser('availableenv', help='Get available env(os, lanuage, ai_arch, os_dep, pip)')
        self._add_account_args(availableenv_parser)
        self._add_availableenv_args(availableenv_parser)

        # A get base image command
        checkbase_parser = subparsers.add_parser('checkbase', help='Check base enviroment exists(os, language, ai_arch_v)')
        self._add_account_args(checkbase_parser)
        self._add_checkbase_args(checkbase_parser)

        # A get translate command
        # translate_parser = subparsers.add_parser('translate', help='Translate (os, language, ai_arch_v)')
        # self._add_account_args(translate_parser)
        # self._add_translate_args(translate_parser)


    def load_params(self):
        self.params = vars(self.parser.parse_args())
        if self.params.has_key('cpu'):
            if self.params['cpu'] < 1 or self.params["cpu"] > 8:
                raise RuntimeError('cpu should be int between 1 to 8, but now:{0}'.format(self.params['cpu']))
        if self.params.has_key('memory'):
            if self.params['memory'] < 1 or self.params["memory"] > 8:
                raise RuntimeError('memory should be int between 1 to 8, but now:{0}'.format(self.params['memory']))
        if self.params.has_key('deploy_weight'):
            if int(self.params['deploy_weight']) < 1 or int(self.params["deploy_weight"]) > 100:
                raise RuntimeError('deploy_weight should be int between 1 to 100, but now:{0}'.format(self.params['deploy_weight']))


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
            'Uai-Params', 'Uai Service Managment Parameters')
        args_parser.add_argument(
            '--service_name',
            type=str,
            required=True,
            help='the uai service name')
        args_parser.add_argument(
            '--cpu',
            type=int,
            required=True,
            help='the number of cpu used by each instance of uai service, int between 1 to 8')
        args_parser.add_argument(
            '--memory',
            type=int,
            required=True,
            help='the number of GB memory used by each instance of uai service, int between 1 to 8')

    def _add_checkbase_args(self, parser):
        args_parser = parser.add_argument_group(
            'Uai-Params', 'Uai Service Managment Parameters')
        args_parser.add_argument(
            '--os',
            type=str,
            default='ubuntu',
            help='the type of the docker os, default as ubuntu')
        args_parser.add_argument(
            '--language',
            type=str,
            default='python-2.7.6',
            help='the language of the docker, default as python-2.7.6')
        args_parser.add_argument(
            '--ai_arch_v',
            type=str,
            # default='tensorflow-1.1.0',
            required=True,
            help='AI architecture and specific version')

    def _add_availableenv_args(self, parser):
        args_parser = parser.add_argument_group(
            'Uai-Params', 'Uai Service Managment Parameters')
        args_parser.add_argument(
            '--pkg_type',
            type=str,
            choices=['os', 'language', 'ai_arch','aptget', 'pip'],
            required=True,
            help='enviroment pakcage type (choose in os, language, ai_arch, aptget, pip)')

    # def _add_checkpip_args(self, parser):
    #     args_parser = parser.add_argument_group(
    #         'Uai-Params', 'Uai Service Managment Parameters')
    #     args_parser.add_argument(
    #         '--pip',
    #         type=str,
    #         help='the dependency of the python pip')

    def _add_pack_args(self, parser):
        code_parse = parser.add_argument_group(
            'Code-Params', 'User Code Storage Info Parameters')
        code_parse.add_argument(
            '--bucket',
            type=str,
            required=True,
            help='the name of ufile bucket')
        code_parse.add_argument(
            '--pack_file_path',
            type=str,
            required=True,
            help='the path to pack files')
        code_parse.add_argument(
            '--upload_name',
            type=str,
            required=True,
            help='the packed tar file name on ufile')
        # code_parse.add_argument(
        #     '--upload_prefix',
        #     type=str,
        #     default='/',
        #     help='the packed tar file prefix on ufile')
        code_parse.add_argument(
            '--main_file',
            type=str,
            required=True,
            help='the main file of the user program')
        code_parse.add_argument(
            '--main_class',
            type=str,
            required=True,
            help='the main class name of the user program')
        code_parse.add_argument(
            '--model_dir',
            type=str,
            required=True,
            help='the model directroy of models')
        code_parse.add_argument(
            '--code_files',
            type=str,
            required=True,
            help='the all python files')
        self.pack_parser = code_parse

        # container_parse = parser.add_argument_group(
        #     'Container-Params', 'Container Enviroment Parameters')
        # container_parse.add_argument(
        #     '--os',
        #     type=str,
        #     default='ubuntu',
        #     help='the type of the docker os')
        # container_parse.add_argument(
        #     '--language',
        #     type=str,
        #     default='python-2.7.6',
        #     help='the language of the docker')
        # container_parse.add_argument(
        #     '--ai_arch_v',
        #     type=str,
        #     # default='tensorflow-1.1.0',
        #     required=True,
        #     help='AI architecture and specific version')
        # container_parse.add_argument(
        #     '--os_deps',
        #     type=str,
        #     # default='',
        #     help='the dependency of the ubuntu apt-get')
        # container_parse.add_argument(
        #     '--pip',
        #     type=str,
        #     # default='',
        #     help='the dependency of the python pip')

    def _add_deploy_args(self, parser):
        args_parser = parser.add_argument_group(
            'Uai-Params', 'Uai Service Managment Parameters')
        args_parser.add_argument(
            '--service_id',
            type=str,
            required=True,
            help='the uai service id, '
                 'which returned as ServiceID when create success ')
        args_parser.add_argument(
            '--deploy_weight',
            type=int,
            default=10,
            help='the weight on grayscale publishing, int between 1 to 100')

        code_parse = parser.add_argument_group(
            'Code-Params', 'User Code Storage Info Parameters')
        code_parse.add_argument(
            '--ufile_url',
            type=str,
            required=True,
            help='the url path given by ufile')
        self.deploy_parser = code_parse

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
            '--os_deps',
            type=str,
            # default='',
            help='the dependency of the ubuntu apt-get')
        container_parse.add_argument(
            '--pip',
            type=str,
            # default='',
            help='the dependency of the python pip')

    def _add_checkprogress_args(self, parser):
        args_parser = parser.add_argument_group(
            'Uai-Params', 'Uai Service Managment Parameters')
        args_parser.add_argument(
            '--service_id',
            type=str,
            required=True,
            help='the uai service id, '
                 'which returned as ServiceID when create success ')
        args_parser.add_argument(
            '--service_version',
            type=str,
            required=True,
            help='the version number of uai service, '
                 'which returned as SrvVersion when deploy success. ')


    def _add_delete_args(self, parser):
        args_parser = parser.add_argument_group(
            'Uai-Params', 'Uai Service Managment Parameters')
        args_parser.add_argument(
            '--service_id',
            type=str,
            required=True,
            help='the uai service id, '
                 'which returned as ServiceID when create success ')

        args_parser.add_argument(
            '--paas_id',
            type=str,
            required=False,
            help='the paas id of uai service, '
                 'which returned as SrvPaasID when create success ')

        args_parser.add_argument(
            '--service_version',
            type=str,
            required=False,
            help='the version number of uai service, '
                 'which returned as SrvVersion when deploy success. '
                 '(Optional, deleting all versions of uai service when not specified)')
        
    def _add_stop_args(self, parser):
        args_parser = parser.add_argument_group(
            'Uai-Params', 'Uai Service Managment Parameters')
        args_parser.add_argument(
            '--service_id',
            type=str,
            required=True,
            help='the uai service id, '
                 'which returned as ServiceID when create success ')

        args_parser.add_argument(
            '--paas_id',
            type=str,
            required=True,
            help='the paas id of uai service, '
                 'which returned as SrvPaasID when create success ')

        args_parser.add_argument(
            '--service_version',
            type=str,
            required=False,
            help='the version number of uai service, '
                 'which returned as SrvVersion when deploy success. '
                 '(Optional, deleting all versions of uai service when not specified)')
        
    def _add_start_args(self, parser):
        args_parser = parser.add_argument_group(
            'Uai-Params', 'Uai Service Managment Parameters')
        args_parser.add_argument(
            '--service_id',
            type=str,
            required=True,
            help='the uai service id, '
                 'which returned as ServiceID when create success ')

        args_parser.add_argument(
            '--paas_id',
            type=str,
            required=True,
            help='the paas id of uai service, '
                 'which returned as SrvPaasID when create success ')

        args_parser.add_argument(
            '--service_version',
            type=str,
            required=True,
            help='the version number of uai service, '
                 'which returned as SrvVersion when deploy success.')

    def _add_listservice_args(self, parser):
        args_parser = parser.add_argument_group(
            'Uai-Params', 'Uai Service Managment Parameters')
        args_parser.add_argument(
            '--service_id',
            type=str,
            required=False,
            help='the uai service id, '
                 'which returned as ServiceID when create success '
                 '(Optional, get all uai services when not specified)')
        
    def _add_listversion_args(self, parser):
        args_parser = parser.add_argument_group(
            'Uai-Params', 'Uai Service Managment Parameters')
        args_parser.add_argument(
            '--service_id',
            type=str,
            required=True,
            help='the uai service id, '
                 'which returned as ServiceID when create success ')
        args_parser.add_argument(
            '--service_version',
            type=str,
            required=False,
            help='the uai service version number, '
                 'which returned as SrvVersion when deploy success '
                 '(Optional, get all versions of an uai service when not specified)')

    def _add_modifyname_args(self, parser):
        args_parser = parser.add_argument_group(
            'Uai-Params', 'Uai Service Managment Parameters')
        args_parser.add_argument(
            '--service_id',
            type=str,
            required=True,
            help='the uai service id, '
                 'which returned as ServiceID when create success ')
        args_parser.add_argument(
            '--service_name',
            type=str,
            required=True,
            help='the uai service name')
        
    def _add_modifyweight_args(self, parser):
        args_parser = parser.add_argument_group(
            'Uai-Params', 'Uai Service Managment Parameters')
        args_parser.add_argument(
            '--service_id',
            type=str,
            required=True,
            help='the uai service id, '
                 'which returned as ServiceID when create success ')
        args_parser.add_argument(
            '--paas_id',
            type=str,
            required=True,
            help='the paas id of uai service, '
                 'which returned as SrvPaasID when create success ')
        args_parser.add_argument(
            '--service_version',
            type=str,
            required=True,
            help='the version number of uai service, '
                 'which returned as SrvVersion when deploy success.')
        args_parser.add_argument(
            '--deploy_weight',
            type=int,
            default=10,
            help='the weight on grayscale publishing, int between 1 to 100')

    # def _add_translate_args(self, parser):
    #     args_parser = parser.add_argument_group(
    #         'Uai-Params', 'Uai Service Managment Parameters')
    #     args_parser.add_argument(
    #         '--os',
    #         type=str,
    #         default='ubuntu',
    #         help='the type of the docker os')
    #     args_parser.add_argument(
    #         '--language',
    #         type=str,
    #         default='python-2.7',
    #         help='the language of the docker')
    #     args_parser.add_argument(
    #         '--ai_arch_v',
    #         type=str,
    #         # default='tensorflow-1.1.0',
    #         required=True,
    #         help='AI architecture and specific version')
    #     args_parser.add_argument(
    #         '--os_deps',
    #         type=str,
    #         # default='',
    #         help='the dependency of the ubuntu apt-get')
    #     args_parser.add_argument(
    #         '--pip',
    #         type=str,
    #         # default='',
    #         help='the dependency of the python pip')

    def _load_conf_params(self):
        """ Config the conf_params from the CMD
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
                    'private_key': self.params['private_key'],
                    'upload_name': self.params['upload_name']
                },
                # 'dockerfile': {
                #     'driver': self.params['ai_arch_v'],
                #     'language': {
                #         'version': self.params['language'].split('-')[1],
                #         'type': self.params['language'].split('-')[0]
                #     },
                #     'os': self.params['os'],
                #     'os-deps':[],
                #     'pip':[]
                # }
            }
        }

    def _load_args(self):
        """ Json param loader
        """
        self._load_conf_params()


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


