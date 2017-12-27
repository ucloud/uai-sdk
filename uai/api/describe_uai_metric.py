from uai.api.base_api import BaseUaiServiceApiOp


class DescribeUAIServiceMetric(BaseUaiServiceApiOp):

    ACTION_NAME = "DescribeResourceMetric"
    """
    DescribeResourceMetric
        Input:
            public_key          string(required) Public key of the user
            private_key         string(required) Private key of the user
            project_id          int(optional)    Project ID of the job
            region              string(optional) Which Region to run the job
            zone                string(optional) Which Zone in the Region to run the job

        Output:
            RetCode         int(required)                Op return code: 0: success, others: error code
            TotalCount      string(required)             the count of result
            Message         string(not required)         Message: error description
            DataSet         []                           the meta information of metric.
    """
    def __init__(self, public_key, private_key, project_id='', region=''):
        super(DescribeUAIServiceMetric, self).__init__(self.ACTION_NAME, public_key, private_key, project_id, region, zone=False)
        self.cmd_params['Region'] = region if region != '' else super(DescribeUAIServiceMetric, self).PARAMS_DEFAULT_REGION
        self.cmd_params['ResourceType'] = 'uaiservice'

    def _check_args(self, params):
        return True

    def call_api(self):
        succ, self.rsp = super(DescribeUAIServiceMetric, self).call_api()
        return succ, self.rsp