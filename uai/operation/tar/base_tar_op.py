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
import sys
import json
import tarfile
from uai.utils.logger import uai_logger
from uai.operation.base_operation import BaseUaiServiceOp

class UaiServiceTarOp(BaseUaiServiceOp):
    """ The Base Tar Tool Class with UAI
    """
    def __init__(self, parser):
        super(UaiServiceTarOp, self).__init__(parser)

        self.conf_params = {}
        self.filelist = []

    def _add_code_args(self, tar_parser):
        code_parse = tar_parser.add_argument_group(
            'Code-Params', 'User Code Storage Info Parameters')
        code_parse.add_argument(
            '--pack_file_path',
            type=str,
            required=True,
            help='the relative directry of files')
        if hasattr(self, 'pack_source') is True:
            code_parse.add_argument(
                '--upload_name',
                type=str,
                required=True,
                help='the packed tar file name')
        else:
            code_parse.add_argument(
                '--tar_name',
                type=str,
                required=True,
                help='the packed tar file name')
        code_parse.add_argument(
            '--main_module',
            type=str,
            required=True,
            help='the main module of the user program')
        code_parse.add_argument(
            '--main_class',
            type=str,
            required=True,
            help='the main class name of the user program')
        code_parse.add_argument(
            '--model_dir',
            type=str,
            required=True,
            help='the directroy of models, relative to the pack_file_path')
        code_parse.add_argument(
            '--code_files',
            type=str,
            required=True,
            help='the all python files')

    def _add_args(self):
        self._add_code_args(self.parser)

    def _parse_code_args(self, args):
        self.pack_file_path = args['pack_file_path']
        if hasattr(self, 'pack_source') is True:
            self.upload_name = args['upload_name']
            self.tar_name = self.upload_name
        else:
            self.tar_name = args['tar_name']

        self.main_file = args['main_module']
        self.main_class =args['main_class']
        self.model_dir = args['model_dir']
        self.code_files = args['code_files']

    def _parse_args(self, args):
        self._parse_code_args(args)

    def _get_filelist(self):
        self._get_code_list()
        self._get_model_list()

    def _get_code_list(self):
        code_filelist = self.code_files.strip().split(',')
        for i in code_filelist:
            self.filelist.append(i)
        self.filelist.append('ufile.json')

    def _get_model_list(self):
        raise UserWarning("UaiPackTool._get_model_list Unimplemented")

    def _gen_jsonfile(self):
        with open(os.path.join(os.getcwd(), self.pack_file_path, 'ufile.json'), 'w') as f:
            json.dump(self.conf_params, f)

    def _pack_file(self):
        uai_logger.info('Start packing files in the target tar path.')
        os.chdir(os.path.join(os.getcwd(), self.pack_file_path))

        tar = tarfile.open(self.tar_name, 'w')
        for i in self.filelist:
            try:
                tar.add(i)
            except OSError as e:
                uai_logger.info('{0} : {1}'.format(OSError, e))
                uai_logger.info('The package process is interrupted.')
                sys.exit(0)
        tar.close()
        uai_logger.info('Finish packing the files.')

    def _tar(self):
        self._get_filelist()
        self._gen_jsonfile()
        self._pack_file()

    def cmd_run(self, args):
        self._parse_args(args)
        self._tar()
