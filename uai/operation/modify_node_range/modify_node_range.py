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

class UaiServiceModifySrvVersionNodeRangeOp(BaseUaiServiceOp):
    """
    The Base Modify Service Version Node Range Class with UAI
    """
    def __init__(self, parser):
        super(UaiServiceModifySrvVersionNodeRangeOp, self).__init__(parser)

    def _add_noderange_args(self, noderange_parser):
        noderange_parse = noderange_parser.add_argument_group(
            'Node-range-Params', 'Node-range Params, help to modify service version node range'
        )
        noderange_parse.add_argument(
            '--service_id',
            type=str,
            required=True,
            help='The service id of UAI Inference',
        )
        noderange_parse.add_argument(
            '--srv_version',
            type=str,
            required=True,
            help='The service version of UAI Inference'
        )
        noderange_parse.add_argument(
            '--node_range_min',
            type=int,
            required=True,
            help='The minimum node count'
        )
        noderange_parse.add_argument(
            '--node_range_max',
            type=int,
            required=True,
            help='The maximum node count'
        )

    def _add_args(self):
        super(UaiServiceModifySrvVersionNodeRangeOp, self)._add_args()
        self._add_noderange_args(self.parser)

    def _parse_noderange_args(self, args):
        self.service_id = args['service_id']
        self.srv_version = args['srv_version']
        self.node_range_min = args['node_range_min']
        self.node_range_max = args['node_range_max']
        if int(self.node_range_min) < 2:
            raise ValueError('Node range min should not be smaller than 2, current node count: {0}'.format(self.node_range_min))
        if int(self.node_range_max) < 2:
            raise ValueError('Node range max should not be smaller than 2, current node count: {0}'.format(self.node_range_max))
        if int(self.node_range_min) > int(self.node_range_max):
            raise ValueError('Node range min (current: {0}) should be smaller than node range max (current: {1})'.format(self.node_range_min, self.node_range_max))

    def _parse_args(self, args):
        super(UaiServiceModifySrvVersionNodeRangeOp, self)._parse_args(args)
        self._parse_noderange_args(args)

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
            node_range_min=self.node_range_min,
            node_range_max=self.node_range_max,
        )

        succ, rsp = modifyOp.call_api()
        if not succ:
            raise RuntimeError('Call  ModifyUAISrvVersionNodeRange error, Error message: {0}'.format(rsp['Message']))
        return succ, rsp
