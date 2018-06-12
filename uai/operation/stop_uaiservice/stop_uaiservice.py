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

from uai.utils.utils import parse_unrequired_args
from uai.operation.base_operation import BaseUaiServiceOp
from uai.api.stop_uai_service import StopUAIServiceApiOp

class UaiServiceStopServiceOp(BaseUaiServiceOp):
    """
    Base Stop Service Tool with UAI
    """

    def __init__(self, parser):
        super(UaiServiceStopServiceOp, self).__init__(parser)

    def __add_stop_args(self, stop_parser):
        stop_parse = stop_parser.add_argument_group(
            'Stop-Params', 'Stop Parameters, help to stop service'
        )
        stop_parse.add_argument(
            '--service_id',
            type=str,
            required=True,
            help='the service id of UAI Inference'
        )
        stop_parse.add_argument(
            '--srv_version',
            type=str,
            required=False,
            help='the service verison of UAI Inference'
        )

    def _add_args(self):
        super(UaiServiceStopServiceOp, self)._add_args()
        self.__add_stop_args(self.parser)

    def _parse_stop_args(self, args):
        self.service_id = args['service_id']
        self.srv_version = parse_unrequired_args('srv_version', args)

    def _parse_args(self, args):
        super(UaiServiceStopServiceOp, self)._parse_args(args)
        self._parse_stop_args(args)

    def cmd_run(self, args):
        self._parse_args(args)

        stopOp = StopUAIServiceApiOp(
            public_key=self.public_key,
            private_key=self.private_key,
            project_id=self.project_id,
            region=self.region,
            zone=self.zone,
            service_id=self.service_id,
            srv_version=self.srv_version,
        )

        succ, rsp = stopOp.call_api()
        if not succ:
            raise RuntimeError('Call  StopUAIService error, Error message: {0}'.format(rsp['Message']))
        return succ, rsp