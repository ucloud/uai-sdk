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
from uai.api.create_uai_service import CreateUAIServiceApiOp
from uai.api.create_uai_exclusive_service import CreateUAIExclusiveServiceApiOp
from uai.api.get_uai_srv_available_resource import GetUAISrvAvailableResourceApiOp

SERVICE_TYPE_CPU = 1
SERVICE_TYPE_GPU = 2

class UaiServiceCreateOp(BaseUaiServiceOp):
    """
    The Base Create Tool Class with UAI
    """
    def __init__(self, parser):
        super(UaiServiceCreateOp, self).__init__(parser)

    def _add_create_args(self, create_parser):
        create_parse = create_parser.add_argument_group(
            'Create-Params', 'Create Parameters, help to create service')
        create_parse.add_argument(
            '--service_name',
            type=str,
            required=True,
            help='The service name of UAI Inference')
        create_parse.add_argument(
            '--cpu',
            type=int,
            choices=[1, 2, 4, 8],
            required=False,
            help='The number of cpu used by each instance of uai service, must be one of [1, 2, 4, 8], required when using cpu')
        create_parse.add_argument(
            '--memory',
            type=int,
            choices=[1, 2, 4, 8, 16],
            required=False,
            help='The number of GB memory, (this value is equal to value of cpu), required when using cpu')
        create_parse.add_argument(
            '--gpu',
            type=str,
            required=False,
            help='The gpu type of created service, required when using gpu(create exclusive service)'
        )
        create_parse.add_argument(
            '--business_group',
            type=str,
            required=False,
            help='The name of business group')

    def _add_args(self):
        super(UaiServiceCreateOp, self)._add_args()
        self._add_create_args(self.parser)


    def _parse_create_args(self, args):
        self.service_name = args['service_name']
        if 'gpu' in args and args['gpu'] != None:
            self.gpu = args['gpu']
            self.cpu = parse_unrequired_args('cpu', args)
            self.memory = parse_unrequired_args('memory', args)
        elif ('cpu' in args and args['cpu'] != None) and ('memory' in args and args['memory'] != None):
            self.gpu = parse_unrequired_args('gpu', args)
            self.cpu = args['cpu']
            self.memory = args['memory']
            if self.cpu != self.memory:
                raise ValueError('Value of "cpu" and "memory" should be equal when creating elastic services, Current cpu:{0} memory:{1}'.format(self.cpu, self.memory))
        else:
            raise ValueError('Parameters "cpu, memory" and "gpu" should not be nil at same time.')
        self.business_group = parse_unrequired_args('business_group', args)

    def _parse_args(self, args):
        super(UaiServiceCreateOp, self)._parse_args(args)
        if not self._parse_create_args(args):
            return False
        return True

    def _get_ability_id(self):
        abilityOp = GetUAISrvAvailableResourceApiOp(
            public_key=self.public_key,
            private_key=self.private_key,
            project_id=self.project_id,
            region=self.region,
            zone=self.zone,
            service_type=SERVICE_TYPE_GPU
        )
        succ, result = abilityOp.call_api()
        if not succ:
            raise RuntimeError("Call GetUAISrvAvailableResource error, Error message: {0}".format(result['Message']))
        srv_nodes = result['DataSet']
        for srv_node in srv_nodes:
            if srv_node['NodeName'] == self.gpu:
                ability_id = srv_node['NodeId']
                ability_cpu = srv_node['CPU']
                ability_mem = srv_node['Memory']
                if (self.cpu != '' and self.cpu != ability_cpu) or (self.memory != '' and self.memory != ability_mem):
                    raise ValueError("GPU ability match error, current choice is \'{0}C{1}G\',  practical is \'{2}C{3}G\'".format(self.cpu, self.memory, ability_cpu, ability_mem))
                return ability_id
        raise ValueError("Current GPU:{0} is not supported".format(self.gpu))

    def cmd_run(self, args):
        self._parse_args(args)

        if self.gpu == '':
            createOp = CreateUAIServiceApiOp(
                public_key=self.public_key,
                private_key=self.private_key,
                project_id=self.project_id,
                region=self.region,
                zone=self.zone,
                srv_name=self.service_name,
                cpu=self.cpu,
                memory=self.memory,
                business_group=self.business_group,
            )
            succ, rsp = createOp.call_api()
            if not succ:
                raise RuntimeError ("Call CreateUAIService error, Error message: {0}".format(rsp["Message"]))
        else:
            self.bill_prod_id = self._get_ability_id()

            createOp = CreateUAIExclusiveServiceApiOp(
                public_key=self.public_key,
                private_key=self.private_key,
                project_id=self.project_id,
                region=self.region,
                zone=self.zone,
                srv_name=self.service_name,
                bill_prod=self.bill_prod_id,
                business_group=self.business_group,
            )
            succ, rsp = createOp.call_api()
            if not succ:
                raise RuntimeError("Call CreateUAIExclusiveService error, Error message: {0}".format(rsp["Message"]))
        return succ, rsp