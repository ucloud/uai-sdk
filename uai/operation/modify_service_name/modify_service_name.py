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

from uai.operation.base_operation import BaseUaiServiceOp
from uai.api.modify_uai_srv_name import ModifyUAISrvNameApiOp

class UaiServiceModifyServiceNameOp(BaseUaiServiceOp):
    """
    The Base Modify Service Name Class with UAI
    """
    def __init__(self, parser):
        super(UaiServiceModifyServiceNameOp, self).__init__(parser)

    def _add_name_args(self, name_parser):
        name_parse = name_parser.add_argument_group(
            'Name-Params', 'Modify Service Name Parameters, help to modify service name'
        )
        name_parse.add_argument(
            '--service_id',
            type=str,
            required=True,
            help='The service id of UAI Inference')
        name_parse.add_argument(
            '--service_name',
            type=str,
            required=True,
            help='The modified service name of UAI Inference')

    def _add_args(self):
        super(UaiServiceModifyServiceNameOp, self)._add_args()
        self._add_name_args(self.parser)

    def _parse_name_args(self, args):
        self.service_id = args['service_id']
        self.service_name = args['service_name']

    def _parse_args(self, args):
        super(UaiServiceModifyServiceNameOp, self)._parse_args(args)
        self._parse_name_args(args)

    def cmd_run(self, args):
        self._parse_args(args)

        modifyOp = ModifyUAISrvNameApiOp(
            public_key=self.public_key,
            private_key=self.private_key,
            project_id=self.project_id,
            region=self.region,
            zone=self.zone,
            service_id=self.service_id,
            srv_name=self.service_name
        )

        succ, rsp = modifyOp.call_api()
        if not succ:
            raise RuntimeError('Call  ModifyUAISrvName error, Error message: {0}'.format(rsp['Message']))
        return succ, rsp
