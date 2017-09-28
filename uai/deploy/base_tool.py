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
import argparse
import json
import time
import requests
from uai.utils.utils import _verfy_ac
from uai.utils.logger import uai_logger
from uai.arch_conf.base_conf import *
from uai.utils.retcode_checker import *
from uai.cmd.base_cmd import *

CHECK_PROGRESS_MAX_STEPS = 200
CHECK_PROGRESS_WAIT_SECONDS = 5
DEPLOY_ID_FILE = './deploy_id.log'

class UaiDeployTool(object):
    """ The Base Deploy Tool Class with UAI
    """
    def __init__(self, platform, parser):
        self.platform = platform
        self.parser = parser
        self.conf_params = {}
        # self.request_params = {}
        # self.check_params = {}

        self._add_args()
        self.id_file = open(DEPLOY_ID_FILE, 'w')

    def _add_args(self):
        """ AI Arch Specific Deploy Tool should implement its own _add_args
        """
        raise UserWarning("UaiDeployTool._add_args Unimplemented")

    def _load_args(self):
        """ AI Arch Specific Pack Tool should implement its own _load_args
        """
        raise UserWarning("UaiPackTool._load_args Unimplemented")

    def pack(self):
        """ AI Arch Specific Pack Tool should implement its own _load_args
        """
        raise UserWarning("UaiPackTool._load_args Unimplemented")

    def deploycmd(self):
        self.deployTool = UaiCmdTool(argparse.ArgumentParser())
        sys.argv = ['any', 'deploy']
        for k in self.params.keys():
            if k == 'public_key' or k == 'private_key' \
                    or k == 'os' or k == 'language' or k == 'ai_arch_v' or k == 'os_deps' or k == 'pip' \
                    or k=='bucket' or k=='ufile_name' or k=='service_id' or k == 'deploy_weight':
                if self.params[k]:
                    sys.argv.append('--' + k)
                    sys.argv.append(self.params[k])
        # self.deployTool.cmd(self.params)
        self.deployTool.cmd()
        self.service_version = self.deployTool.rsp['SrvVersion']

    def checkprogress(self):
        self.checkProgressTool = UaiCmdTool(argparse.ArgumentParser())
        sys.argv = ['any', 'checkprogress', '--service_version', self.service_version]
        for k in self.params.keys():
            if k == 'public_key' or k == 'private_key' \
                    or k == 'service_id':
                sys.argv.append('--' + k)
                sys.argv.append(self.params[k])
        print(sys.argv)
        # self.checkProgressTool.cmd(self.params)
        self.checkProgressTool.cmd()

    def deploy(self):
        self._load_args()
        if not self.params['ufile_name']:
            self.pack()
            self.params['ufile_name'] = self.params['upload_name']
        self.deploycmd()
        for i in range(0, CHECK_PROGRESS_MAX_STEPS):
            self.checkprogress()
            if self.checkProgressTool.rsp['Status'] == 'Error' \
                    or self.checkProgressTool.rsp['Status'] == 'Started' \
                    or self.checkProgressTool.rsp['Status'] == 'ToStart':
                break
            time.sleep(CHECK_PROGRESS_WAIT_SECONDS)
