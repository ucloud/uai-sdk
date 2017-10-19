from uai.operation.base_operation import BaseUaiServiceOp
from uai.api.modify_uai_srv_version_weight import ModifyUAISrvVersionWeightOp


class UaiServiceModifyWeightOp(BaseUaiServiceOp):
    def __init__(self, parser):
        super(UaiServiceModifyWeightOp, self).__init__(parser)

    def _add_args(self, parser):
        super(UaiServiceModifyWeightOp, self)._add_args(parser)
        args_parser = parser.add_argument_group()
        args_parser.add_argument(
            '--service_id',
            type=str,
            required=True,
            help='the uai service id')

        args_parser.add_argument(
            '--paas_id',
            type=str,
            required=True,
            help='the paas id of uai service')

        args_parser.add_argument(
            '--service_version',
            type=str,
            required=True,
            help='the version number of uai service')

        args_parser.add_argument(
            '--deploy_weight',
            type=int,
            default=10,
            required=True,
            help='the weight on grayscale publishing, int between 1 to 100')
        # add other params in subclasses#

    def _parse_args(self):
        super(UaiServiceModifyWeightOp, self)._parse_args()
        self.srv_version = self.params['service_version'] if 'service_version' in self.params else ''
        self.service_id = self.params['service_id'] if 'service_id' in self.params else ''
        self.srv_paas_id = self.params['paas_id'] if 'paas_id' in self.params else ''
        self.deploy_weight = self.params['deploy_weight'] if 'deploy_weight' in self.params else ''
        if self.deploy_weight > 100 or self.deploy_weight < 0:
            raise RuntimeError('the param deploy_weight must be between 1 and 100')
        # add other params in subclasses#

    def cmd_run(self, params):
        super(UaiServiceModifyWeightOp, self).cmd_run(params)
        modifyOp = ModifyUAISrvVersionWeightOp(public_key=self.public_key,
                                      private_key=self.private_key,
                                      project_id=self.project_id,
                                      region=self.region,
                                      zone=self.zone,
                                      service_id=self.service_id,
                                      srv_paas_id=self.srv_paas_id,
                                      srv_version=self.srv_version,
                                      deploy_weight=self.deploy_weight)
        succ, rsp = modifyOp.call_api()
        return succ, rsp