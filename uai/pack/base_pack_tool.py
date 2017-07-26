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
import argparse
import tarfile
from datetime import datetime
from ucloud.ufile import putufile
from uai.utils.logger import uai_logger
from uai.cmd.base_cmd import UaiCmdTool

UFILE_INFO = './ufile_info.log'

class UaiPackTool(object):
    """ The Base Pack Tool Class with UAI
    """
    def __init__(self, platform, parser):
        self.platform = platform
        self.parser = parser

        self.conf_params = {}
        self.filelist = []
        
        self._add_args()

        self.ufile_info = open(UFILE_INFO, 'w')

    def _add_args(self):
        """ AI Arch Specific Pack Tool should implement its own _add_args
        """
        raise UserWarning("UaiPackTool._add_args Unimplemented")
        
    def _load_args(self):
        """ AI Arch Specific Pack Tool should implement its own _load_args
        """
        raise UserWarning("UaiPackTool._load_args Unimplemented")

    def _analysis_args(self):
        self.config.load_params()
        if self.config.params.has_key("ai_arch_v"):
            if self.platform != self.config.params["ai_arch_v"].lower().split('-')[0]:
                raise RuntimeError("ai_arch_v should be one version of " + self.platform)

    def _get_filelist(self):
        """ Get list of the files in the package
        """
        self._get_code_list()
        self._get_model_list()

    def _get_code_list(self):
        code_filelist = self.conf_params['docker']['ufile']['code_files']
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
        uai_logger.info('Generating uflie.json in filepath: {0}'.format(self.params['pack_file_path']))
        self.conf_params['docker']['ufile']['files'] = [self.params['upload_name']]
        self.conf_params['docker']['ufile'].pop('code_files')
        self.conf_params['docker']['ufile'].pop('model_dir')
        self.conf_params['docker']['ufile'].pop('upload_name')
        #self.conf_params['docker']['ufile'].pop('upload_prefix')

        with open(os.path.join(self.params['pack_file_path'], 'ufile.json'), 'w') as f:
            json.dump(self.conf_params, f)

    def _pack_file(self):
        """ Pack files in the target path
        """
        uai_logger.info('Start packing files in the target pack path.')
        os.chdir(self.params['pack_file_path'])

        tar = tarfile.open(self.params['upload_name'], 'w')
        for i in self.filelist:
            try:
                tar.add(i)
            except OSError, e:
                uai_logger.info('{0} : {1}'.format(OSError, e))
                uai_logger.info('The package process is interrupted.')
                sys.exit(0)
        
        uai_logger.info('Finish packing the files.')

    def _upload_file(self):
        """ Upload tar file to certain bucket
        """
        public_key = self.conf_params['docker']['ufile']['public_key']
        private_key = self.conf_params['docker']['ufile']['private_key']
        bucket = self.conf_params['docker']['ufile']['bucket']

        uai_logger.debug('Start upload file to the bucket {0}'.format(bucket))
        handler = putufile.PutUFile(public_key, private_key)
        local_file = os.path.join(self.params['pack_file_path'], self.params['upload_name'])
        key = self.params['upload_name']
        uai_logger.info('Upload >> key: {0}, local file: {1}'.format(key, local_file))
        ret, resp = handler.putfile(bucket, key, local_file)
        uai_logger.debug('Ufile response: {0}'.format(resp))
        assert resp.status_code == 200, 'upload seems something error'
        uai_logger.debug('upload local file :{0} to ufile key= {1} successful'.
                     format(local_file, key))

        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.ufile_info.write('Upload Time: {0}\n'.format(current_time))
        self.ufile_info.write('Path of Upload File: {0}\n'.format(key))

    def _translate_args(self):
        # self.translateTool = UaiCmdTool(argparse.ArgumentParser())
        # sys.argv = ['any', 'translate']
        # for k in self.params.keys():
        #     if k=='public_key' or k== 'private_key' \
        #             or k == 'os' or k =='language' or k=='ai_arch_v' or k=='os_deps' or k=='pip':
        #         if self.params[k]:
        #             sys.argv.append('--' + k)
        #             sys.argv.append(self.params[k])
        # self.translateTool._load_args()
        self.translateTool = UaiCmdTool(self.parser)
        self.translateTool.conf_params = self.config.params
        self.translateTool.translate_pkg_params()
        self.conf_params['os'] = self.translateTool.conf_params['os']
        self.conf_params['language'] = self.translateTool.conf_params['language']
        self.conf_params['ai_arch_v'] = self.translateTool.conf_params['ai_arch_v']
        if self.translateTool.conf_params['os_deps']:
            self.conf_params['os_deps'] = self.translateTool.conf_params['os_deps']
        else:
            self.conf_params['os_deps'] = ""
        if self.translateTool.conf_params['pip']:
            self.conf_params['pip'] = self.translateTool.conf_params['pip']
        else:
            self.conf_params['pip'] = ""


    def pack(self):
        self._load_args()
        self._get_filelist()
        self._gen_jsonfile()
        self._pack_file()
        self._upload_file()