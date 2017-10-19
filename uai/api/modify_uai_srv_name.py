from uai.api.base_api import BaseUaiServiceApiOp


class ModifyUAISrvNameOp(BaseUaiServiceApiOp):

    ACTION_NAME = "ModifyUAISrvName"

    def __init__(self, public_key, private_key, service_id, srv_name, project_id='', region='', zone=''):
        super(ModifyUAISrvNameOp, self).__init__(self.ACTION_NAME, public_key, private_key, project_id, region, zone)
        self.cmd_params['Region'] = region if region != '' else super(ModifyUAISrvNameOp, self).PARAMS_DEFAULT_REGION
        self.cmd_params['ServiceID'] = service_id
        self.cmd_params['SrvName'] = srv_name

    def _check_args(self, params):
        if params['ServiceID'] == '':
            return False
        if params['SrvName'] == '':
            return False
        return True

    def call_api(self):
        succ, self.rsp = super(ModifyUAISrvNameOp, self).call_api()
        return succ, self.rsp