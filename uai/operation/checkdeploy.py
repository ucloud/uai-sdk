from uai.operation.base_operation import BaseUaiServiceOp
from uai.api.check_uai_deploy_progress import CheckUAIDeployProgressOp

class UaiServiceCheckDeployOp(BaseUaiServiceOp):

    def __init__(self, parser):
        super(UaiServiceCheckDeployOp, self).__init__(parser)

    def _add_args(self, parser):
        super(UaiServiceCheckDeployOp, self)._add_args(parser)
        args_parser = parser.add_argument_group()
        args_parser.add_argument(
            '--service_id',
            type=str,
            required=True,
            help='the uai service id')
        args_parser.add_argument(
            '--service_version',
            type=str,
            required=True,
            help='the version number of uai service ')
        #add other params in subclasses#

    def _parse_args(self):
        super(UaiServiceCheckDeployOp, self)._parse_args()
        self.srv_version = self.params['service_version'] if 'service_version' in self.params else ''
        self.service_id = self.params['service_id'] if 'service_id' in self.params else ''
        # add other params in subclasses#

    def cmd_run(self, params):
        super(UaiServiceCheckDeployOp, self).cmd_run(params)
        checkDeployOp = CheckUAIDeployProgressOp(public_key=self.public_key,
                                            private_key=self.private_key,
                                            project_id=self.project_id,
                                            region=self.region,
                                            zone=self.zone,
                                            service_id=self.service_id,
                                            srv_version=self.srv_version)
        succ, rsp = checkDeployOp.call_api()
        return succ, rsp