from uai.api.base_api import BaseUaiServiceApiOp


class GetUAIServiceListOp(BaseUaiServiceApiOp):

    ACTION_NAME = "GetUAIServiceList"

    def __init__(self, public_key, private_key, project_id='', region='', zone='', service_id='',offset=0, limit=0):
        super(GetUAIServiceListOp, self).__init__(self.ACTION_NAME, public_key, private_key, project_id, region, zone)
        self.cmd_params['Region'] = region if region != '' else super(GetUAIServiceListOp, self).PARAMS_DEFAULT_REGION
        self.cmd_params['ServiceID'] = service_id
        self.cmd_params['Offset'] = offset
        self.cmd_params['Limit'] = limit
        # add other params in subclasses#

    def _check_args(self, params):
        return

    def call_api(self):
        succ, self.rsp = super(GetUAIServiceListOp, self).call_api()
        return succ, self.rsp






