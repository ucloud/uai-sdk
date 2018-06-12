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

from uai.operation.packdocker.base_packdocker_op import UaiServiceDockerPackOp

class UaiServiceSelfDockerPackOp(UaiServiceDockerPackOp):
    """
    Self-defined Doceker Pack Tool Class
    """
    def __init__(self, parser):
        super(UaiServiceSelfDockerPackOp, self).__init__(parser)

    def _add_self_args(self, packdocker_parser):
        self_parse = packdocker_parser.add_argument_group(
            'Self-defined-Params', 'Self-defined Parameters, help to build docker images'
        )
        self_parse.add_argument(
            '--bimg_name',
            type=str,
            required=True,
            help='The base image to build docker image'
        )
        self_parse.add_argument(
            '--pack_file_path',
            type=str,
            required=True,
            help='The relative directry of files'
        )
        self_parse.add_argument(
            '--conf_file',
            type=str,
            required=True,
            help='The name of config file'
        )

    def _add_args(self):
        self._add_uhub_args(self.parser)
        self._add_self_args(self.parser)

    def _parse_self_args(self, args):
        self.baseimage = args['bimg_name']
        self.pack_file_path = args['pack_file_path']
        self.conf_file = args['conf_file']

    def _parse_args(self, args):
        self._parse_uhub_args(args)
        self._parse_self_args(args)
        return True

    def cmd_run(self, args):
        if self._parse_args(args) == False:
            return False
        self._bulid_userimage()
        self._push_userimage()
