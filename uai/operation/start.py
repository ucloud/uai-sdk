from uai.operation.base_operation import BaseUaiServiceOp
from uai.api.start_uai_service import StartUAIServiceOp


class UaiServiceStartOp(BaseUaiServiceOp):
    def __init__(self, parser):
        super(UaiServiceStartOp, self).__init__(parser)

    def _add_args(self, parser):
        super(UaiServiceStartOp, self)._add_args(parser)
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

    def _parse_args(self):
        super(UaiServiceStartOp, self)._parse_args()
        # add other params in subclasses#

    def cmd_run(self, params):
        super(UaiServiceStartOp, self).cmd_run(params)
        startOp = StartUAIServiceOp(public_key=self.public_key,
                                      private_key=self.private_key,
                                      project_id=self.project_id,
                                      region=self.region,
                                      zone=self.zone,
                                      service_id=self.params['service_id'],
                                      srv_paas_id=self.params['paas_id'],
                                      srv_version=self.params['service_version'])
        succ, rsp = startOp.call_api()
        return succ, rsp