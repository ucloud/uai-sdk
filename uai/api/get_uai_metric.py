from uai.api.base_api import BaseUaiServiceApiOp


class GetUAIServiceMetric(BaseUaiServiceApiOp):

    ACTION_NAME = "GetMetric"
    """
    GetMetric
        Input:
            public_key          string(required) Public key of the user
            private_key         string(required) Private key of the user
            project_id          int(optional)    Project ID of the job
            region              string(optional) Which Region to run the job
            zone                string(optional) Which Zone in the Region to run the job
            service_id          string(required) Which service to get metric info
            metric_list         list(required) the metric list, you can get it from DescribeResourceMetric api.
            beg_time            int(required) the begin time of metric info.(unix time)
            end_time            int(required) the begin time of metric info.(unix time)

        Output:
            RetCode         int(required)                Op return code: 0: success, others: error code
            TotalCount      string(required)             the count of result
            Message         string(not required)         Message: error description
            DataSet         []                           the detailed information of metric
    """
    def __init__(self, public_key, private_key, service_id, metric_list, beg_time, end_time, project_id='', region=''):
        super(GetUAIServiceMetric, self).__init__(self.ACTION_NAME, public_key, private_key, project_id, region, zone=False)
        self.cmd_params['Region'] = region if region != '' else super(GetUAIServiceMetric, self).PARAMS_DEFAULT_REGION
        self.cmd_params['ResourceType'] = 'uaiservice'
        self.cmd_params['ResourceId'] = service_id
        self.cmd_params['BeginTime'] = beg_time
        self.cmd_params['EndTime'] = end_time
        self.cmd_params['MetricName'] = metric_list

    def _check_args(self, params):
        if self.cmd_params["ResourceId"] == "" or type(self.cmd_params["ResourceId"]) != str:
            raise RuntimeError("resource_id shoud be <str> and is not nil.")
        if type(self.cmd_params["BeginTime"]) != int:
            raise RuntimeError("beg_time shoud be <int>.")
        if type(self.cmd_params["EndTime"]) != int:
            raise RuntimeError("end_time shoud be <int>.")

        if self.cmd_params["BeginTime"] > self.cmd_params["EndTime"]:
            raise RuntimeError("end_time should be  greater than beg_time. end_time: {0}, beg_time: {1}".
                               format(self.cmd_params["EndTime"], self.cmd_params["BeginTime"]))

        if type(self.cmd_params['MetricName']) != list:
            raise RuntimeError("metric_list shoud be <list>. The elem of list is metric, you can get them from describe_uai_metric api.")

        for i, value in enumerate(self.cmd_params['MetricName']):
            metric_name = 'MetricName.{0}' .format(i)
            self.cmd_params[metric_name] = value
        del self.cmd_params['MetricName']
        return True

    def call_api(self):
        succ, self.rsp = super(GetUAIServiceMetric, self).call_api()
        return succ, self.rsp