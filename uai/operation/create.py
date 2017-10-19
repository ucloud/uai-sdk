from uai.operation.base_operation import BaseUaiServiceOp
from uai.api.create_uai_service import CreateUAIServiceOp

class UaiServiceCreateOp(BaseUaiServiceOp):

    def __init__(self, parser):
        super(UaiServiceCreateOp, self).__init__(parser)

    def _add_args(self, parser):
        super(UaiServiceCreateOp, self)._add_args(parser)
        args_parser = parser.add_argument_group()
        args_parser.add_argument(
            '--service_name',
            type=str,
            required=True,
            help='the uai service name')
        args_parser.add_argument(
            '--cpu',
            type=int,
            choices=[1, 2, 4, 8],
            required=True,
            help='the number of cpu used by each instance of uai service, must be one of [1, 2, 4, 8]')
        args_parser.add_argument(
            '--memory',
            type=int,
            choices=[1, 2, 4, 8],
            required=True,
            help='the number of GB memory, (this value is equal to value of cpu)')
        args_parser.add_argument(
            '--business_group',
            type=str,
            required=False,
            help='the name of business group')
        #add other params in subclasses#

    def _parse_args(self):
        super(UaiServiceCreateOp, self)._parse_args()
        self.srv_name = self.params['service_name'] if 'service_name' in self.params else ''
        self.cpu =  self.params['cpu'] if 'cpu' in self.params else ''
        self.memory = self.params['memory'] if 'memory' in self.params else ''
        # add other params in subclasses#

    def cmd_run(self, params):
        super(UaiServiceCreateOp, self).cmd_run(params)
        createOp = CreateUAIServiceOp(public_key=self.public_key,
                                      private_key=self.private_key,
                                      project_id=self.project_id,
                                      region=self.region,
                                      zone=self.zone,
                                      srv_name=self.srv_name,
                                      cpu=self.cpu,
                                      memory=self.memory)
        succ, rsp = createOp.call_api()
        return succ, rsp
        # add other params in subclasses#