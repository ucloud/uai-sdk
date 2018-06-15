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
from uai.api.delete_uai_service import DeleteUAIServiceApiOp

class UaiServiceDeleteOp(BaseUaiServiceOp):
    """
    The Base Delete Tool Class with UAI
    """
    def __init__(self, parser):
        super(UaiServiceDeleteOp, self).__init__(parser)

    def _add_delete_args(self, delete_parser):
        delete_parse = delete_parser.add_argument_group(
            "Delete-Params", "Delete Parameters, help to delete service")
        delete_parse.add_argument(
            '--service_id',
            type=str,
            required=True,
            help='The service id to be deleted'
        )
        delete_parse.add_argument(
            '--srv_version',
            type=str,
            required=False,
            help='The service version to be deleted'
        )

    def _add_args(self):
        super(UaiServiceDeleteOp, self)._add_args()
        self._add_delete_args(self.parser)

    def _parse_delete_args(self, args):
        self.service_id = args['service_id']
        self.srv_version = parse_unrequired_args('srv_version', args)

    def _parse_args(self, args):
        super(UaiServiceDeleteOp, self)._parse_args(args)
        self._parse_delete_args(args)

    def cmd_run(self, args):
        self._parse_args(args)

        deleteOp = DeleteUAIServiceApiOp(
            public_key=self.public_key,
            private_key=self.private_key,
            project_id=self.project_id,
            region=self.region,
            zone=self.zone,
            service_id=self.service_id,
            srv_version=self.srv_version,
        )

        succ, rsp = deleteOp.call_api()
        if not succ:
            raise RuntimeError('Call DeleteUAIService error, Error message: {0}'.format(rsp['Message']))
        return succ, rsp
