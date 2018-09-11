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


class BaseUAITrainOp(object):
    """Base Class for UAI Train Op"""
    def __init__(self, parser):
        self.parser = parser
        self._add_args()

    def _add_account_args(self, parser):
        args_parser = parser.add_argument_group(
                         'User-Params', 'User Authentication Parameters')
        args_parser.add_argument(
            '--public_key',
            type=str,
            required=True,
            help='The public key of the user')
        args_parser.add_argument(
            '--private_key',
            type=str,
            required=True,
            help='The private key of the user')
        args_parser.add_argument(
            '--project_id',
            type=str,
            required=False,
            help='The project id of ucloud, could be null')
        args_parser.add_argument(
            '--region',
            type=str,
            required=False,
            help='The region to run the task, could be null')
        args_parser.add_argument(
            '--zone',
            type=str,
            required=False,
            help='The zone to run the task, could be null')


    def _parse_account_args(self, args):
        self.pub_key = args['public_key']
        self.pri_key = args['private_key']
        if 'project_id' in args and args['project_id'] != None:
            self.project_id = args['project_id']
        else:
            self.project_id = ""
        if 'region' in args and args['region'] != None:
            self.region = args['region']
        else:
            self.region = ""
        if 'zone' in args and args['zone'] != None:
            self.zone = args['zone']
        else:
            self.zone = ""
        return True

    def _add_args(self):
        self._add_account_args(self.parser)

    def _parse_args(self, args):
        self._parse_account_args(args)
