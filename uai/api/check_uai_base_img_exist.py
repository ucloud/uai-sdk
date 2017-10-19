from uai.api.base_api import BaseUaiServiceApiOp


class CheckUAIBaseImgExistOp(BaseUaiServiceApiOp):

    ACTION_NAME = "CheckUAIBaseImgExist"

    def __init__(self, public_key, private_key, os_version, python_version, ai_frame_version, os_deps='', pip='', project_id='', region='', zone=''):
        super(CheckUAIBaseImgExistOp, self).__init__(self.ACTION_NAME, public_key, private_key, project_id, region, zone)
        self.cmd_params['Region'] = region if region != '' else super(CheckUAIBaseImgExistOp, self).PARAMS_DEFAULT_REGION
        self.cmd_params['OSVersion'] = os_version
        self.cmd_params['PythonVersion'] = python_version
        self.cmd_params['AIFrameVersion'] = ai_frame_version

        self.cmd_params['AptGetPKGID.0'] = ''
        self.cmd_params['PipPKGID.0'] = ''
        # add other params in subclasses#

    def _check_args(self, params):
        if params['OSVersion'] == '':
            return False
        if params['PythonVersion'] == '':
            return False
        if params['AIFrameVersion'] == '':
            return False
        return True

    def call_api(self):
        succ, self.rsp = super(CheckUAIBaseImgExistOp, self).call_api()
        return succ, self.rsp







