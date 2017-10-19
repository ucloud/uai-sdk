from uai.api.base_api import BaseUaiServiceApiOp

class GetUAISrvBillInfo(BaseUaiServiceApiOp):

    ACTION_NAME = "GetUAISrvBillInfo"

    def __init__(self, public_key, private_key, begin_time, end_time, project_id='', region='', zone='', offset=0, limit=0):
        super(GetUAISrvBillInfo, self).__init__(self.ACTION_NAME, public_key, private_key, project_id, region, zone)
        self.cmd_params['Region'] = region if region != '' else super(GetUAISrvBillInfo, self).PARAMS_DEFAULT_REGION
        self.cmd_params['BeginTime'] = begin_time
        self.cmd_params['EndTime'] = end_time

        self.cmd_params['Offset'] = offset
        self.cmd_params['Limit'] = limit

    def _check_args(self, params):
        if params['BeginTime'] == '':
            return False
        if params['EndTime'] == '':
            return False

        return True

    def call_api(self):
        succ, self.rsp = super(GetUAISrvBillInfo, self).call_api()
        return succ, self.rsp