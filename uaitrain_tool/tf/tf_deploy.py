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
import os
import argparse
import time

from uaitrain.pack.tf_pack_tool import TFPackTool
from uaitrain.cmd.base_cmd import UaiCmdTool

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='AI TensorFlow Arch Deployer',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    tf_tool = TFPackTool(parser)
    tf_tool._analysis_args()
    if tf_tool.config.params["commands"] == "pack":
        tf_tool.pack()
    elif tf_tool.config.params["commands"] == "deploy":
        cmd_tool = UaiCmdTool(parser)
        cmd_tool.conf_params = tf_tool.config.params
        cmd_tool.translate_pkg_params()
        cmd_tool.cmd()

        time.sleep(10)
        # check progress
        check_tool = UaiCmdTool(argparse.ArgumentParser())
        sys.argv = ['any', 'checkprogress', '--service_version', cmd_tool.rsp['SrvVersion']]
        for k in cmd_tool.conf_params.keys():
            if k=='public_key' or k=='private_key' or k=='service_id':
                sys.argv.append('--' + k)
                sys.argv.append(cmd_tool.conf_params[k])
        for i in range(0, 200):
            cmd_tool.cmd()
            if cmd_tool.rsp['Status'] == 'Error' \
                    or cmd_tool.rsp['Status'] == 'Started' \
                    or cmd_tool.rsp['Status'] == 'ToStart':
                break
            time.sleep(10)
    else:
        cmd_tool = UaiCmdTool(parser)
        cmd_tool.conf_params = tf_tool.config.params
        cmd_tool.cmd()

