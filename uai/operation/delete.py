from uai.operation.base_operation import BaseUaiServiceOp
from uai.api.delete_uai_service import DeleteUAIServiceOp

class UaiServiceDeleteOp(BaseUaiServiceOp):

    def __init__(self, parser):
        super(UaiServiceDeleteOp, self).__init__(parser)

    def _add_args(self, parser):
        super(UaiServiceDeleteOp, self)._add_args(parser)

        args_parser = parser.add_argument_group()
        args_parser.add_argument(
            '--service_id',
            type=str,
            required=True,
            help='the uai service id')
        
        args_parser.add_argument(
            '--paas_id',
            type=str,
            required=False,
            help='the paas id of uai service')

        args_parser.add_argument(
            '--service_version',
            type=str,
            required=False,
            help='the version number of uai service, '
                 '(Optional, deleting all versions of uai service when not specified)')
        #add other params in subclasses#

    def _parse_args(self):
        super(UaiServiceDeleteOp, self)._parse_args()
        self.service_id = self.params['service_id'] if 'service_id' in self.params else ''
        self.srv_paas_id = self.params['paas_id'] if 'paas_id' in self.params else ''
        self.srv_version = self.params['service_version'] if 'service_version' in self.params else ''
        # add other params in subclasses#

    def cmd_run(self, params):
        super(UaiServiceDeleteOp, self).cmd_run(params)
        deleteOp = DeleteUAIServiceOp(public_key=self.public_key,
                                    private_key=self.private_key,
                                    project_id=self.project_id,
                                    region=self.region,
                                    zone=self.zone,
                                    service_id=self.service_id,
                                    srv_paas_id=self.srv_paas_id,
                                    srv_version=self.srv_version)
        succ, rsp = deleteOp.call_api()
        return succ, rsp