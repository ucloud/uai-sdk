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

from uai.deploy.tf_tool import TFDeployTool

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='AI TensorFlow Arch Deployer',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    tf_deploy_tool = TFDeployTool(parser)
    tf_deploy_tool.deploy()
