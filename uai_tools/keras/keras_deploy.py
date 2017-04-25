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

from uai.deploy.keras_tool import KerasDeployTool

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='AI Keras Arch Deployer',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    keras_deploy_tool = KerasDeployTool(parser)
    keras_deploy_tool.deploy()
