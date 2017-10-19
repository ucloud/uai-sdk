import time
from uai.operation.base_operation import BaseUaiServiceOp
from uai.api.get_uai_srv_bill_info import GetUAISrvBillInfo


class UaiServiceGetUAISrvBillInfoOp(BaseUaiServiceOp):
    def __init__(self, parser):
        super(UaiServiceGetUAISrvBillInfoOp, self).__init__(parser)

    def _add_args(self, parser):
        super(UaiServiceGetUAISrvBillInfoOp, self)._add_args(parser)
        args_parser = parser.add_argument_group(
            'Uai-Params', 'Uai Service Managment Parameters')

        args_parser.add_argument(
            '--begin_time',
            type=str,
            required=True,
            help='begin time')
        args_parser.add_argument(
            '--end_time',
            type=str,
            required=True,
            help='end time')
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
         # add other params in subclasses#

    def datetime_timestamp(self, dt):
        try:
            s = time.mktime(time.strptime(dt, '%Y-%m-%d %H:%M:%S'))
            return int(s)
        except Exception as e:
            raise RuntimeError('time format error, the time fomat should be %Y-%m-%d %H:%M:%S, such as 2017-03-28-6:53:40')

    def _parse_args(self):
        super(UaiServiceGetUAISrvBillInfoOp, self)._parse_args()
        self.begin_time = self.datetime_timestamp(self.params['begin_time']) if 'begin_time' in self.params else ''
        self.end_time = self.datetime_timestamp(self.params['end_time']) if 'end_time' in self.params else ''
        self.offset = self.params['offset'] if 'offset' in self.params else ''
        self.limit = self.params['limit'] if 'limit' in self.params else ''
        # add other params in subclasses#

    def cmd_run(self, params):
        super(UaiServiceGetUAISrvBillInfoOp, self).cmd_run(params)
        getEnvOp = GetUAISrvBillInfo(public_key=self.public_key,
                                      private_key=self.private_key,
                                      project_id=self.project_id,
                                      region=self.region,
                                      zone=self.zone,
                                      begin_time=self.begin_time,
                                      end_time=self.end_time,
                                      offset=self.offset,
                                      limit=self.limit)
        succ, rsp = getEnvOp.call_api()
        return succ, rsp
