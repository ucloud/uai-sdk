from uai.operation.base_operation import BaseUaiServiceOp
from uai.api.get_uai_srv_version_list import GetUAISrvVersionListOp

class UaiSrvVersionListOp(BaseUaiServiceOp):

    def __init__(self, parser):
        super(UaiSrvVersionListOp, self).__init__(parser)

    def _add_args(self, parser):
        super(UaiSrvVersionListOp, self)._add_args(parser)
        args_parser = parser.add_argument_group()
        args_parser.add_argument(
            '--service_id',
            type=str,
            required=True,
            help='the uai service id')
        args_parser.add_argument(
            '--service_version',
            type=str,
            required=False,
            help='the version number of uai service '
                 '(get all version when not specified)')

        args_parser.add_argument(
            '--offset',
            type=int,
            required=False,
            default=0,
            help='the begin position of the version list, '
                 '(Optional, default as 0, return list from beginning)')
        args_parser.add_argument(
            '--limit',
            type=int,
            required=False,
            default=10,
            help='the total number of the version list to return, '
                 '(Optional, default as 10, return 10 version of the version list)')
        #add other params in subclasses#

    def _parse_args(self):
        super(UaiSrvVersionListOp, self)._parse_args()

        self.srv_version = self.params['service_version'] if 'service_version' in self.params else ''
        self.service_id = self.params['service_id'] if 'service_id' in self.params else ''
        self.offset = self.params['offset'] if 'offset' in self.params else ''
        self.limit = self.params['limit'] if 'limit' in self.params else ''
        # add other params in subclasses#

    def cmd_run(self, params):
        super(UaiSrvVersionListOp, self).cmd_run(params)

        listVersionOp = GetUAISrvVersionListOp(public_key=self.public_key,
                                            private_key=self.private_key,
                                            project_id=self.project_id,
                                            region=self.region,
                                            zone=self.zone,
                                            service_id=self.service_id,
                                            srv_version=self.srv_version,
                                            offset=self.offset,
                                            limit=self.limit)
        succ, rsp = listVersionOp.call_api()
        return succ, rsp