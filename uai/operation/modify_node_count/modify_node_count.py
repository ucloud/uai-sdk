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
from uai.api.modify_uai_srv_version_node_range import ModifyUAISrvVersionNodeRangeApiOp

class UaiServiceModifySrvVersionNodeCountOp(BaseUaiServiceOp):
    """
    The Base Modify Service Version Node Count Class with UAI
    """
    def __init__(self, parser):
        super(UaiServiceModifySrvVersionNodeCountOp, self).__init__(parser)

    def _add_nodset_args(self, nodeset_parser):
        nodeset_parse = nodeset_parser.add_argument_group(
            'Node-range-Params', 'Node-range Params, help to modify service version node range'
        )
        nodeset_parse.add_argument(
            '--service_id',
            type=str,
            required=True,
            help='The service id of UAI Inference',
        )
        nodeset_parse.add_argument(
            '--srv_version',
            type=str,
            required=True,
            help='The service version of UAI Inference'
        )
        nodeset_parse.add_argument(
            '--node_count',
            type=int,
            required=True,
            help='The modified node count'
        )

    def _add_args(self):
        super(UaiServiceModifySrvVersionNodeCountOp, self)._add_args()
        self._add_nodset_args(self.parser)

    def _parse_nodeset_args(self, args):
        self.service_id = args['service_id']
        self.srv_version = args['srv_version']
        self.node_count = args['node_count']
        if int(self.node_count) < 2:
            raise ValueError('Node count should not be smaller than 2, current node count: {0}'.format(self.node_count))

    def _parse_args(self, args):
        super(UaiServiceModifySrvVersionNodeCountOp, self)._parse_args(args)
        self._parse_nodeset_args(args)

    def cmd_run(self, args):
        self._parse_args(args)

        modifyOp = ModifyUAISrvVersionNodeRangeApiOp(
            public_key=self.public_key,
            private_key=self.private_key,
            project_id=self.project_id,
            region=self.region,
            zone=self.zone,
            service_id=self.service_id,
            srv_version=self.srv_version,
            node_range_min=self.node_count,
            node_range_max=self.node_count,
        )

        succ, rsp = modifyOp.call_api()
        if not succ:
            raise RuntimeError('Call  ModifyUAISrvVersionNodeRange error, Error message: {0}'.format(rsp['Message']))
        return succ, rsp
