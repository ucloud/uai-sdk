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
from uai.operation.tar.base_tar_op import UaiServiceTarOp

class UaiServiceMxnetTarOp(UaiServiceTarOp):
    """ MXNet Tar Tool Class
    """
    def __init__(self, parser):
        super(UaiServiceMxnetTarOp, self).__init__(parser)

    def _add_model_args(self, tar_parser):
        model_parse = tar_parser.add_argument_group(
            'Model-Params', 'User Model Storage Info Parameters')
        model_parse.add_argument(
            '--model_name',
            type=str,
            required=True,
            help='the MXNet model name')
        model_parse.add_argument(
            '--num_epoch',
            type=int,
            required=True,
            help='the num of the model ckpt epoch')

    def _add_args(self):
        super(UaiServiceMxnetTarOp, self)._add_args()
        self._add_model_args(self.parser)

    def _parse_model_args(self, args):
        self.model_name = args['model_name']
        self.num_epoch = args['num_epoch']
        self.model_prefix = os.path.join(self.model_dir, self.model_name)
        self.conf_params['http_server'] = {
            'exec': {
                'main_file': self.main_file,
                'main_class': self.main_class
            },
            'mxnet': {
                'model_dir': self.model_dir,
                'model_name': self.model_name,
                "num_epoch": self.num_epoch
            }
        }

    def _parse_args(self, args):
        super(UaiServiceMxnetTarOp, self)._parse_args(args)
        self._parse_model_args(args)

    def _get_model_list(self):
        self.model_arch_file = self.model_prefix + '-' + 'symbol'+ '.json'
        num_epoch = str(self.num_epoch).zfill(4)
        self.model_weight_file = self.model_prefix + '-' + num_epoch + '.params'
        self.filelist.append(self.model_arch_file)
        self.filelist.append(self.model_weight_file)
