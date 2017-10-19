from uai.api.base_api import BaseUaiServiceApiOp


class GetUAISrvVersionListOp(BaseUaiServiceApiOp):

    ACTION_NAME = "GetUAISrvVersionList"

    def __init__(self, public_key, private_key, project_id='', region='', zone='', service_id='', srv_version='', offset=0, limit=0):
        super(GetUAISrvVersionListOp, self).__init__(self.ACTION_NAME, public_key, private_key, project_id, region, zone)
        self.cmd_params['Region'] = region if region != '' else super(GetUAISrvVersionListOp, self).PARAMS_DEFAULT_REGION
        self.cmd_params['ServiceID'] = service_id

        self.cmd_params['SrvVersion'] = srv_version
        self.cmd_params['Offset'] = offset
        self.cmd_params['Limit'] = limit

    def _check_args(self, params):
        if params['ServiceID'] == '':
            return False
        return True

    def call_api(self):
        succ, self.rsp = super(GetUAISrvVersionListOp, self).call_api()
        return succ, self.rsp