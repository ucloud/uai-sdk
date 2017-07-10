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

import sys
import time
import argparse
from base_tool import UaiDeployTool
from uai.arch_conf.keras_conf import KerasJsonConf

class KerasDeployTool(UaiDeployTool):
    """ Keras Deploy Tool class  
    """
    def __init__(self, parser):
        super(KerasDeployTool, self).__init__('keras', parser)

    def _add_args(self):
        """ Keras specific _add_args tool to parse Keras params through KerasJsonConf
        """
        self.config = KerasJsonConf(self.parser)

    def _load_args(self):
        self.config.load_params()
        self.conf_params = self.config.get_conf_params()
        self.params = self.config.get_arg_params()

    def pack(self):
        self.packTool = KerasJsonConf(argparse.ArgumentParser())
        if self.params['upload_name'] == "uaiserivce.tar":
            self.params['upload_name'] = time.strftime('%Y-%m-%d_%X', time.localtime()) + ".tar"

        sys.argv = ['any', 'pack']
        for k in self.params.keys():
            if k == 'public_key' or k == 'private_key' \
                    or k == 'os' or k == 'language' or k == 'ai_arch_v' or k == 'os_deps' or k == 'pip' \
                    or k=='bucket' or k=='pack_file_path' \
                    or k=='main_file' or k=='main_class' or k=='model_dir' or k=='code_files' or k=='model_name' \
                    or k == 'upload_name' \
                    or k=='all_one_file' or k=='model_arch_type':
                sys.argv.append('--' + k)
                sys.argv.append(self.params[k])
        self.packTool.pack()


    def deploy(self):
        super(KerasDeployTool, self).deploy()
