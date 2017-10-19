from uai.operation.base_operation import BaseUaiServiceOp
from uai.api.modify_uai_srv_name import ModifyUAISrvNameOp


class UaiServiceModifyServiceNameOp(BaseUaiServiceOp):
    def __init__(self, parser):
        super(UaiServiceModifyServiceNameOp, self).__init__(parser)

    def _add_args(self, parser):
        super(UaiServiceModifyServiceNameOp, self)._add_args(parser)
        args_parser = parser.add_argument_group()
        args_parser.add_argument(
            '--service_id',
            type=str,
            required=True,
            help='the uai service id that you will modify')

        args_parser.add_argument(
            '--service_name',
            type=str,
            required=True,
            help='the uai service name')
        # add other params in subclasses#

    def _parse_args(self):
        super(UaiServiceModifyServiceNameOp, self)._parse_args()
        # add other params in subclasses#

    def cmd_run(self, params):
        super(UaiServiceModifyServiceNameOp, self).cmd_run(params)
        modifyOp = ModifyUAISrvNameOp(public_key=self.public_key,
                                      private_key=self.private_key,
                                      project_id=self.project_id,
                                      region=self.region,
                                      zone=self.zone,
                                      service_id=self.params['service_id'],
                                      srv_name=self.params['service_name'])
        succ, rsp = modifyOp.call_api()
        return succ, rsp