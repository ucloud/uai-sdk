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
    """ The Base Pack Tool Class with UAI
    """
    def __init__(self, parser):
        super(UaiServiceTarOp, self).__init__(parser)
        self.conf_params = {}
        self.filelist = []

    def _add_args(self, parser):
        super(UaiServiceTarOp, self)._add_args(parser)
        code_parse = parser.add_argument_group(
            'Code-Params', 'User Code Storage Info Parameters')
        # code_parse.add_argument(
        #     '--ai_frame_type',
        #     type=str,
        #     choices=['tensorflow', 'keras', 'mxnet', 'caffe'],
        #     required=True,
        #     help='the ai frame type (you can choose from [tensorflow, keras, mxnet, caffe])')
        code_parse.add_argument(
            '--pack_file_path',
            type=str,
            required=True,
            help='the path to tar files')
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
            help='the model directroy of models')
        code_parse.add_argument(
            '--code_files',
            type=str,
            required=True,
            help='the all python files')
        #add other params in subclasses#

    def _parse_args(self):
        super(UaiServiceTarOp, self)._parse_args()

        self.pack_file_path = self.params['pack_file_path']
        if hasattr(self, 'pack_source') is True:
            self.upload_name = self.params['upload_name']
            self.tar_name = self.upload_name
        else:
            self.tar_name = self.params['tar_name']
        self.main_file = self.params['main_module']
        self.main_class = self.params['main_class']
        self.model_dir = self.params['model_dir']
        self.code_files = self.params['code_files']

    def _get_filelist(self):
        """ Get list of the files in the package
        """
        self._get_code_list()
        self._get_model_list()

    def _get_code_list(self):
        code_filelist = self.code_files.strip().split(',')
        for i in code_filelist:
            self.filelist.append(i)
        self.filelist.append('ufile.json')

    def _get_model_list(self):
        """ AI Arch Specific Pack Tool should implement its own _get_filelist
        """
        raise UserWarning("UaiPackTool._get_model_list Unimplemented")

    def _gen_jsonfile(self):
        """ Reformat the conf params and generate jsonfile
        """
        with open(os.path.join(self.pack_file_path, 'ufile.json'), 'w') as f:
            json.dump(self.conf_params, f)

    def _pack_file(self):
        """ Pack files in the target path
        """
        uai_logger.info('Start packing files in the target tar path.')
        os.chdir(self.pack_file_path)

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

    def cmd_run(self, params):
        super(UaiServiceTarOp, self).cmd_run(params)
        self._tar()