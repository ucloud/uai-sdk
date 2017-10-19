from uai.api.base_api import BaseUaiServiceApiOp


class GetUAIAvailableEnvPkgOp(BaseUaiServiceApiOp):

    ACTION_NAME = "GetUAIAvailableEnvPkg"

    def __init__(self, public_key, private_key, pkg_type='', project_id='', region='', zone=''):
        super(GetUAIAvailableEnvPkgOp, self).__init__(self.ACTION_NAME, public_key, private_key, project_id, region, zone)
        self.cmd_params['Region'] = region if region != '' else super(GetUAIAvailableEnvPkgOp, self).PARAMS_DEFAULT_REGION
        self.cmd_params['PkgType'] = pkg_type

    def _check_args(self, params):
        return True

    def call_api(self):
        succ, self.rsp = super(GetUAIAvailableEnvPkgOp, self).call_api()
        return succ, self.rsp







