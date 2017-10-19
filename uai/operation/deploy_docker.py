import time
from uai.operation.base_operation import BaseUaiServiceOp
from uai.operation.checkdeploy import CheckUAIDeployProgressOp
from uai.api.deploy_uai_service_by_docker import DeployUAIServiceByDocker


class UaiServiceDeployOp(BaseUaiServiceOp):
    def __init__(self, parser):
        super(UaiServiceDeployOp, self).__init__(parser)

    def _add_args(self, parser):
        super(UaiServiceDeployOp, self)._add_args(parser)
        args_parser = parser.add_argument_group()
        args_parser.add_argument(
            '--service_id',
            type=str,
            required=True,
            help='the uai service id')
        args_parser.add_argument(
            '--image_name',
            type=str,
            required=True,
            help='the image name of Uhub, '
                 'which will be run when deploy success.')

        args_parser.add_argument(
            '--deploy_weight',
            type=str,
            required=False,
            default=10,
            help='the version weight of uai service, '
                 '(Optional, default is 10 when not specified)')

        args_parser.add_argument(
            '--description',
            type=str,
            required=False,
            help='the version description of uai service, '
                 '(Optional)')
        # add other params in subclasses#

    def _parse_args(self):
        super(UaiServiceDeployOp, self)._parse_args()
        self.service_id = self.params['service_id']
        self.image_name = self.params['image_name']
        self.deploy_weight = self.params['deploy_weight'] if 'deploy_weight' in self.params else ''
        self.description = self.params['description'] if 'description' in self.params else ''
        # add other params in subclasses#

    def cmd_run(self, params):
        super(UaiServiceDeployOp, self).cmd_run(params)
        startOp = DeployUAIServiceByDocker(public_key=self.public_key,
                                      private_key=self.private_key,
                                      project_id=self.project_id,
                                      region=self.region,
                                      zone=self.zone,
                                      service_id=self.service_id,
                                      image_name=self.image_name,
                                      deploy_weight=self.deploy_weight,
                                      srv_v_info=self.description)
        succ, rsp = startOp.call_api()
        if succ == False:
            return False, rsp

        for i in range(0, 200):
            deploy_process_succ, deploy_process_rsp = CheckUAIDeployProgressOp(public_key=self.public_key,
                                                          private_key=self.private_key,
                                                          project_id=self.project_id,
                                                          service_id=self.service_id,
                                                          srv_version=rsp['SrvVersion']).call_api()
            if deploy_process_succ == False \
                    or deploy_process_rsp['Status'] == 'Error' \
                    or deploy_process_rsp['Status'] == 'Started' \
                    or deploy_process_rsp['Status'] == 'ToStart':
                break
            time.sleep(10)
        return succ, rsp