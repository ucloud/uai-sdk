from uai.api.base_api import BaseUaiServiceApiOp


class CreateUAIServiceOp(BaseUaiServiceApiOp):

    ACTION_NAME = "CreateUAIService"

    def __init__(self, public_key, private_key, srv_name, cpu, memory, business_group='', project_id='', region='', zone=''):
        super(CreateUAIServiceOp, self).__init__(self.ACTION_NAME, public_key, private_key, project_id, region, zone)
        self.cmd_params['Region'] = region if region != '' else super(CreateUAIServiceOp, self).PARAMS_DEFAULT_REGION
        self.cmd_params['SrvName'] = srv_name
        self.cmd_params['CPU'] = cpu
        self.cmd_params['Memory'] = memory

        self.cmd_params['BusinessGroup'] = business_group if business_group != '' else self.PARAMS_DEFAULT_BUSINESSGROUP
        # add other params in subclasses#

    def _check_args(self, params):

        if params['SrvName'] == '':
            return False
        if 'CPU' in params and params['CPU'] != '':
            if int(params['CPU']) < 1 or int(params["CPU"]) > 8:
                print('cpu should be int between 1 to 8, but now:{0}'.format(params['CPU']))
                return False
        if 'Memory' in params and params['Memory'] != '':
            if int(params['Memory']) < 1 or int(params["Memory"]) > 8:
                print ('memory should be int between 1 to 8, but now:{0}'.format(params['Memory']))
                return False
        if params['CPU'] != params['Memory']:
            print ('the value of cpu should be equal to memory , but now:cpu is {0}, memory is {1}'.
                   format(params['CPU'], params['Memory']))
            return False

        return True

    def call_api(self):
        succ, self.rsp = super(CreateUAIServiceOp, self).call_api()
        return succ, self.rsp






