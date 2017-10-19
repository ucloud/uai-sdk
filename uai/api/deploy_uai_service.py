from uai.api.base_api import BaseUaiServiceApiOp

class DeployUAIService(BaseUaiServiceApiOp):

    ACTION_NAME = "DeployUAIService"

    def __init__(self, public_key, private_key, service_id, os_version, python_v, ai_frame_v, ufile_url,
                 apt_list='', pip_list='', version_info='', deploy_weight='', project_id='', region='', zone=''):
        super(DeployUAIService, self).__init__(self.ACTION_NAME, public_key, private_key, project_id, region, zone)
        self.cmd_params['Region'] = region if region != '' else super(DeployUAIService, self).PARAMS_DEFAULT_REGION
        self.cmd_params['ServiceID'] = service_id
        self.cmd_params['OSVersion'] = os_version
        self.cmd_params['PythonVersion'] = python_v
        self.cmd_params['AIFrameVersion'] = ai_frame_v
        self.cmd_params['UfileBucket'], self.cmd_params['UfileName'] = self.parse_ufile_url(
            ufile_url)
        self.cmd_params['UfileURL'] = ufile_url

        self.cmd_params['DeployWeight'] = deploy_weight
        self.cmd_params['SrvVerMemo'] = version_info

        if len(apt_list) != 0:
            i = 0
            for aptgetid in apt_list:
                self.cmd_params['AptGetPKGID.' + str(i) ] = aptgetid
                i = i + 1
        else:
            self.cmd_params['AptGetPKGID.0'] = ''

        if len(pip_list):
            i = 0
            for pipid in pip_list:
                self.cmd_params['PipPKGID.' + str(i) ] = pipid
                i = i + 1
        else:
            self.cmd_params['PipPKGID.0'] = ''

    def parse_ufile_url(self, url):
        bucket = url[url.find('://') + 3: url.find('.')]
        parturl = url.split('.ufileos.com/')
        if len(parturl) > 1:
            region = parturl[0][parturl[0].find('.') + 1: ]
        if url.find('?') > 0:
            filename = url[url.rfind('/') + 1: url.find('?')]
        else:
            filename = url[url.rfind('/') + 1:]

        return bucket, filename

    def _check_args(self, params):
        if params['ServiceID'] == '':
            return False

        if 'DeployWeight' in params and params['DeployWeight'] != '':
            if int(params['DeployWeight']) < 1 or int(params["DeployWeight"]) > 100:
                print ('deploy_weight should be int between 1 to 100, but now:{0}'.format(params['DeployWeight']))
                return False
        return True

    def call_api(self):
        succ, rsp = super(DeployUAIService, self).call_api()
        return succ, rsp