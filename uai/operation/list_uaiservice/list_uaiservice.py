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
from uai.api.get_uai_service_list import GetUAIServiceListApiOp

class UaiServiceListServiceOp(BaseUaiServiceOp):
    """
    The Base List Service Tool Class with UAI
    """
    def __init__(self, parser):
        super(UaiServiceListServiceOp, self).__init__(parser)

    def _add_service_args(self, service_parser):
        service_parse = service_parser.add_argument_group(
            'Service-Params', 'Service Parameters, help to list service')
        service_parse.add_argument(
            '--service_id',
            type=str,
            required=False,
            help='the service id of UAI Inference'
        )
        service_parse.add_argument(
            '--offset',
            type=int,
            default=0,
            help='list offset'
        )
        service_parse.add_argument(
            '--limit',
            type=int,
            default=0,
            help='list limit'
        )

    def _add_args(self):
        super(UaiServiceListServiceOp, self)._add_args()
        self._add_service_args(self.parser)

    def _parse_service_args(self, args):
        self.service_id = parse_unrequired_args('service_id', args)
        self.offset = parse_unrequired_args('offset', args)
        self.limit = parse_unrequired_args('limit', args)
        if int(self.limit) < 0:
            raise ValueError('Limit should be positive, current limit: {0}'.format(self.limit))
        if int(self.offset) < 0:
            raise ValueError('Offset should be positive, current offset: {0}'.format(self.offset))

    def _parse_args(self, args):
        super(UaiServiceListServiceOp, self)._parse_args(args)
        self._parse_service_args(args)

    def cmd_run(self, args):
        self._parse_args(args)

        listOp = GetUAIServiceListApiOp(
            public_key=self.public_key,
            private_key=self.private_key,
            project_id=self.project_id,
            region=self.region,
            zone=self.zone,
            service_id=self.service_id,
            offset=self.offset,
            limit=self.limit
        )

        succ, rsp = listOp.call_api()
        if not succ:
            raise RuntimeError('Call GetUAIServiceList error, Error message: {0}'.format(rsp['Message']))
        return succ, rsp
