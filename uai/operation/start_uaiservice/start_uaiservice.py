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
from uai.api.start_uai_service import StartUAIServiceApiOp

class UaiServiceStartServiceOp(BaseUaiServiceOp):
    """
    Base Start Service Tool with UAI
    """
    def __init__(self, parser):
        super(UaiServiceStartServiceOp, self).__init__(parser)

    def __add_start_args(self, start_parser):
        start_parse = start_parser.add_argument_group(
            'Start-Params', 'Start Parameters, help to start service'
        )
        start_parse.add_argument(
            '--service_id',
            type=str,
            required=True,
            help='the service id of UAI Inference'
        )
        start_parse.add_argument(
            '--srv_version',
            type=str,
            required=True,
            help='the service verison of UAI Inference'
        )

    def _add_args(self):
        super(UaiServiceStartServiceOp, self)._add_args()
        self.__add_start_args(self.parser)

    def _parse_start_args(self, args):
        self.service_id = args['service_id']
        self.srv_version = args['srv_version']

    def _parse_args(self, args):
        super(UaiServiceStartServiceOp, self)._parse_args(args)
        self._parse_start_args(args)

    def cmd_run(self, args):
        self._parse_args(args)

        startOp = StartUAIServiceApiOp(
            public_key=self.public_key,
            private_key=self.private_key,
            project_id=self.project_id,
            region=self.region,
            zone=self.zone,
            service_id=self.service_id,
            srv_version=self.srv_version,
        )

        succ, rsp = startOp.call_api()
        if not succ:
            raise RuntimeError('Call  StartUAIService error, Error message: {0}'.format(rsp['Message']))
        return succ, rsp
