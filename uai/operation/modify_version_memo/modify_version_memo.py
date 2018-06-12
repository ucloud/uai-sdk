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
from uai.api.modify_uai_srv_version_memo import ModifyUAISrvVersionMemoApiOp

class UaiServiceModifySrvVersionMemoOp(BaseUaiServiceOp):
    """
    Base Modify Version Memo Tool Class with UAI
    """
    def __int__(self, parser):
        super(UaiServiceModifySrvVersionMemoOp, self).__init__(parser)

    def _add_memo_args(self, memo_parser):
        memo_parse = memo_parser.add_argument_group(
            'Memo-Params', 'Modify Version Memo Parameters, help to modify version memo'
        )
        memo_parse.add_argument(
            '--service_id',
            type=str,
            required=True,
            help='the service id of UAI Inference'
        )
        memo_parse.add_argument(
            '--srv_version',
            type=str,
            required=True,
            help='the service version of UAI Inference'
        )
        memo_parse.add_argument(
            '--srv_version_memo',
            type=str,
            required=True,
            help='the modified service version memo of UAI Inference'
        )

    def _add_args(self):
        super(UaiServiceModifySrvVersionMemoOp, self)._add_args()
        self._add_memo_args(self.parser)

    def _parse_memo_args(self, args):
        self.service_id = args['service_id']
        self.srv_version = args['srv_version']
        self.srv_version_memo = args['srv_version_memo']

    def _parse_args(self, args):
        super(UaiServiceModifySrvVersionMemoOp, self)._parse_args(args)
        self._parse_memo_args(args)

    def cmd_run(self, args):
        self._parse_args(args)

        modifyOp = ModifyUAISrvVersionMemoApiOp(
            public_key=self.public_key,
            private_key=self.private_key,
            project_id=self.project_id,
            region=self.region,
            zone=self.zone,
            service_id=self.service_id,
            srv_version=self.srv_version,
            srv_version_memo=self.srv_version_memo
        )

        succ, rsp = modifyOp.call_api()
        if not succ:
            raise RuntimeError('Call  ModifyUAISrvVersionMemo error, Error message: {0}'.format(rsp['Message']))
        return succ, rsp
