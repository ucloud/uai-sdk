from uai.operation.base_operation import BaseUaiServiceOp
from uai.api.get_uai_service_list import GetUAIServiceListOp

class UaiServiceListServiceOp(BaseUaiServiceOp):

    def __init__(self, parser):
        super(UaiServiceListServiceOp, self).__init__(parser)

    def _add_args(self, parser):
        super(UaiServiceListServiceOp, self)._add_args(parser)
        args_parser = parser.add_argument_group()
        args_parser.add_argument(
            '--service_id',
            type=str,
            required=False,
            help='the uai service id, '
                 '(Optional, get all uai services when not specified)')
        args_parser.add_argument(
            '--offset',
            type=int,
            required=False,
            default=0,
            help='the begin position of the service list, '
                 '(Optional, default as 0, return list from beginning)')
        args_parser.add_argument(
            '--limit',
            type=int,
            required=False,
            default=10,
            help='the total number of the service list to return, '
                 '(Optional, default as 10, return 10 service of the service list)')
        #add other params in subclasses#

    def _parse_args(self):
        super(UaiServiceListServiceOp, self)._parse_args()
        self.service_id = self.params['service_id'] if 'service_id' in self.params else ''
        self.offset = self.params['offset'] if 'offset' in self.params else ''
        self.limit = self.params['limit'] if 'limit' in self.params else ''
        # add other params in subclasses#

    def cmd_run(self, params):
        super(UaiServiceListServiceOp, self).cmd_run(params)
        listServiceOp = GetUAIServiceListOp(public_key=self.public_key,
                                            private_key=self.private_key,
                                            project_id=self.project_id,
                                            region=self.region,
                                            zone=self.zone,
                                            service_id=self.service_id,
                                            offset=self.params['offset'],
                                            limit=self.params['limit'])
        succ, rsp = listServiceOp.call_api()
        return succ, rsp