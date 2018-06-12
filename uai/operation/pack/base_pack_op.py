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
from datetime import datetime
from uai.utils.logger import uai_logger
from ucloud.ufile import putufile
from uai.operation.base_operation import BaseUaiServiceOp
from uai.operation.tar.base_tar_op import UaiServiceTarOp

UFILE_INFO = './ufile_info.log'
CURRENT_PATH = os.getcwd()

class UaiServicePackOp(UaiServiceTarOp):
    """ The Base Pack Tool Class with UAI
    """
    def __init__(self, parser):
        super(UaiServicePackOp, self).__init__(parser)

        self.conf_params = {}
        self.filelist = []
        self.ufile_info = []
        self.platform = ''

    def _add_ufile_args(self, pack_parser):
        ufile_parse = pack_parser.add_argument_group(
            'Ufile-Params', 'Ufile Parameters, help to upload file to Ufile automatically'
        )
        ufile_parse.add_argument(
            '--bucket',
            type=str,
            required=True,
            help='the name of ufile bucket')

    def _add_args(self):
        super(UaiServicePackOp, self)._add_args()
        self._add_account_args(self.parser)
        self._add_ufile_args(self.parser)

    def _parse_args(self, args):
        super(UaiServicePackOp, self)._parse_args(args)
        self._parse_account_args(args)
        if "ai_arch_v" in args:
            if self.platform != args["ai_arch_v"].lower().split('-')[0]:
                raise RuntimeError("ai_arch_v should be one version of " + self.platform)
        self.bucket = args['bucket']

    def _upload_to_ufile(self):
        public_key = self.public_key
        private_key = self.private_key
        bucket = self.bucket

        uai_logger.debug('Start upload file to the bucket {0}'.format(bucket))
        handler = putufile.PutUFile(public_key, private_key)
        local_file = os.path.join(CURRENT_PATH, self.pack_file_path, self.upload_name)
        local_file = local_file.replace('\\', '/')
        key = self.upload_name
        uai_logger.info('Upload >> key: {0}, local file: {1}'.format(key, local_file))
        ret, resp = handler.putfile(bucket, key, local_file)
        uai_logger.debug('Ufile response: {0}'.format(resp))
        assert resp.status_code == 200, 'upload seems something error'
        uai_logger.debug('upload local file :{0} to ufile key= {1} successful'.
                         format(local_file, key))

        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.ufile_info.append('Upload Time: {0}\n'.format(current_time))
        self.ufile_info.append('Path of Upload File: {0}\n'.format(key))

    def _pack(self):
        self._upload_to_ufile()
        with open(UFILE_INFO, 'w') as f:
            f.write(''.join(self.ufile_info))

    def cmd_run(self, args):
        self._parse_args(args)
        super(UaiServicePackOp, self).cmd_run(args)
        self._pack()