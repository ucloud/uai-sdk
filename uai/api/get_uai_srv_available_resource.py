from uai.api.base_api import BaseUaiServiceApiOp


class GetUAISrvAvailableResource(BaseUaiServiceApiOp):

    ACTION_NAME = "GetUAISrvAvailableResource"

    def __init__(self, public_key, private_key, project_id='', region='', zone=''):
        super(GetUAISrvAvailableResource, self).__init__(self.ACTION_NAME, public_key, private_key, project_id, region, zone)
        self.cmd_params['Region'] = region if region != '' else super(GetUAISrvAvailableResource, self).PARAMS_DEFAULT_REGION
        # add other params in subclasses#

    def _check_args(self, params):
        return

    def call_api(self):
        succ, self.rsp = super(GetUAISrvAvailableResource, self).call_api()
        return succ, self.rsp






