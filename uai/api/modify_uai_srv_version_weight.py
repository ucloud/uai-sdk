from uai.api.base_api import BaseUaiServiceApiOp


class ModifyUAISrvVersionWeightOp(BaseUaiServiceApiOp):

    ACTION_NAME = "ModifyUAISrvVersionWeight"

    def __init__(self, public_key, private_key, service_id, srv_paas_id, srv_version, deploy_weight, project_id='', region='', zone=''):
        super(ModifyUAISrvVersionWeightOp, self).__init__(self.ACTION_NAME, public_key, private_key, project_id, region, zone)
        self.cmd_params['Region'] = region if region != '' else super(ModifyUAISrvVersionWeightOp, self).PARAMS_DEFAULT_REGION
        self.cmd_params['ServiceID'] = service_id
        self.cmd_params['SrvPaasID'] = srv_paas_id
        self.cmd_params['SrvVersion'] = srv_version
        self.cmd_params['DeployWeight'] = deploy_weight

    def _check_args(self, params):
        if params['ServiceID'] == '':
            return False
        if params['SrvPaasID'] == '':
            return False
        if params['SrvVersion'] == '':
            return False
        if params['DeployWeight'] == '':
            return False
        return True

    def call_api(self):
        succ, self.rsp = super(ModifyUAISrvVersionWeightOp, self).call_api()
        return succ, self.rsp






