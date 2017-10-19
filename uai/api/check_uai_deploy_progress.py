from uai.api.base_api import BaseUaiServiceApiOp


class CheckUAIDeployProgressOp(BaseUaiServiceApiOp):

    ACTION_NAME = "CheckUAIDeployProgress"

    def __init__(self, public_key, private_key, service_id, srv_version, project_id='', region='', zone=''):
        super(CheckUAIDeployProgressOp, self).__init__(self.ACTION_NAME, public_key, private_key, project_id, region, zone)
        self.cmd_params['Region'] = region if region != '' else super(CheckUAIDeployProgressOp, self).PARAMS_DEFAULT_REGION
        self.cmd_params['ServiceID'] = service_id
        self.cmd_params['SrvVersion'] = srv_version
        # add other params in subclasses#

    def _check_args(self, params):
        if params['ServiceID'] == '':
            return False
        if params['SrvVersion'] == '':
            return False
        return True

    def call_api(self):
        succ, self.rsp = super(CheckUAIDeployProgressOp, self).call_api()
        return succ, self.rsp







