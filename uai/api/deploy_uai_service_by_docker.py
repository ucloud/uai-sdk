from uai.api.base_api import BaseUaiServiceApiOp

class DeployUAIServiceByDocker(BaseUaiServiceApiOp):

    ACTION_NAME = "DeployUAIServiceByDocker"

    def __init__(self, public_key, private_key, service_id, image_name, deploy_weight='', srv_v_info='', project_id='', region='', zone=''):
        super(DeployUAIServiceByDocker, self).__init__(self.ACTION_NAME, public_key, private_key, project_id, region, zone)
        self.cmd_params['Region'] = region if region != '' else super(DeployUAIServiceByDocker, self).PARAMS_DEFAULT_REGION
        self.cmd_params['ServiceID'] = service_id
        self.cmd_params['SrvVersion'] = ''

        self.cmd_params['UimgName'] = image_name
        self.cmd_params['DeployWeight'] = deploy_weight
        self.cmd_params['SrvVerMemo'] = srv_v_info

    def _check_args(self, params):
        if params['ServiceID'] == '':
            return False
        if params['UimgName'] == '':
            return False
        if 'DeployWeight' in params and params['DeployWeight'] != '':
            if int(params['DeployWeight']) < 1 or int(params["DeployWeight"]) > 100:
                print ('deploy_weight should be int between 1 to 100, but now:{0}'.format(params['DeployWeight']))
                return False
        return True

    def call_api(self):
        succ, rsp = super(DeployUAIServiceByDocker, self).call_api()
        return succ, rsp






