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
from uai.api.modify_uai_srv_version_weight import ModifyUAISrvVersionWeightApiOp

class UaiServiceModifySrvVersionWeightOp(BaseUaiServiceOp):
    """
    Base Modify Version Weight Tool Class with UAI
    """
    def __int__(self, parser):
        super(UaiServiceModifySrvVersionWeightOp, self).__init__(parser)

    def _add_weight_args(self, weight_parser):
        weight_parse = weight_parser.add_argument_group(
            'Weight-Params', 'Modify Version Weight Parameters, help to modify version weight'
        )
        weight_parse.add_argument(
            '--service_id',
            type=str,
            required=True,
            help='the service id of UAI Inference'
        )
        weight_parse.add_argument(
            '--srv_version',
            type=str,
            required=True,
            help='the service version of UAI Inference'
        )
        weight_parse.add_argument(
            '--deploy_weight',
            type=int,
            required=True,
            help='the modified deploy weight of UAI Inference'
        )

    def _add_args(self):
        super(UaiServiceModifySrvVersionWeightOp, self)._add_args()
        self._add_weight_args(self.parser)

    def _parse_weight_args(self, args):
        self.service_id = args['service_id']
        self.srv_version = args['srv_version']
        self.deploy_weight = args['deploy_weight']
        if int(self.deploy_weight) not in range(1, 100):
            raise ValueError('Deploy weight should be within 1 and 100, current deploy weight: {0}'.format(self.deploy_weight))

    def _parse_args(self, args):
        super(UaiServiceModifySrvVersionWeightOp, self)._parse_args(args)
        self._parse_weight_args(args)

    def cmd_run(self, args):
        self._parse_args(args)

        modifyOp = ModifyUAISrvVersionWeightApiOp(
            public_key=self.public_key,
            private_key=self.private_key,
            project_id=self.project_id,
            region=self.region,
            zone=self.zone,
            service_id=self.service_id,
            srv_version=self.srv_version,
            deploy_weight=self.deploy_weight
        )

        succ, rsp = modifyOp.call_api()
        if not succ:
            raise RuntimeError('Call  ModifyUAISrvVersionWeight error, Error message: {0}'.format(rsp['Message']))
        return succ, rsp