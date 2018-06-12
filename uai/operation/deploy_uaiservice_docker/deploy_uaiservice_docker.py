# Copyright 2017 The UAI-SDK Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import time
from uai.utils.utils import parse_unrequired_args
from uai.operation.base_operation import BaseUaiServiceOp

from uai.api.deploy_uai_service_by_docker import DeployUAIServiceByDockerApiOp
from uai.api.check_uai_deploy_progress import CheckUAIDeployProgressApiOp

class UaiServiceDeployByDockerOp(BaseUaiServiceOp):
    def __init__(self, parser):
        super(UaiServiceDeployByDockerOp, self).__init__(parser)

    def _add_docker_deploy_args(self, docker_deploy_parser):
        docker_deploy_parse =docker_deploy_parser.add_argument_group(
            "Docker-Deploy-Params", "Docker Deploy Parameters, help to deploy uai service by docker")
        docker_deploy_parse.add_argument(
            '--service_id',
            type=str,
            required=True,
            help='The service id of UAI Inference',
        )
        docker_deploy_parse.add_argument(
            '--uimg_name',
            type=str,
            required=True,
            help='The name of user image',

        )
        docker_deploy_parse.add_argument(
            '--deploy_weight',
            type=int,
            default=10,
            help='the deploy weight of current version',

        )
        docker_deploy_parse.add_argument(
            '--srv_version_memo',
            type=str,
            required=False,
            help='the srv version memo of current version',
        )

    def _add_args(self):
        super(UaiServiceDeployByDockerOp, self)._add_args()
        self._add_docker_deploy_args(self.parser)

    def _parse_docker_deploy_args(self, args):
        self.service_id = args['service_id']
        self.uimg_name = args['uimg_name']
        self.deploy_weight = args['deploy_weight']
        if int(self.deploy_weight) not in range(1, 100):
            raise ValueError('Deploy weight should be int within 1 and 100, current deploy weight: {0}'.format(self.deploy_weight))

        self.srv_version_memo = parse_unrequired_args('srv_version_memo', args)

    def _parse_args(self, args):
        super(UaiServiceDeployByDockerOp, self)._parse_args(args)
        self._parse_docker_deploy_args(args)

    def cmd_run(self, args):
        self._parse_args(args)

        deployOp = DeployUAIServiceByDockerApiOp(
            public_key=self.public_key,
            private_key=self.private_key,
            project_id=self.project_id,
            region=self.region,
            zone=self.zone,
            service_id=self.service_id,
            image_name=self.uimg_name,
            deploy_weight=self.deploy_weight,
            srv_v_info=self.srv_version_memo,
        )
        succ, rsp = deployOp.call_api()
        if not succ:
            raise RuntimeError('Call DeployUAIServiceByDocker error, Error message: {0}'.format(rsp['Message']))

        for i in range(0, 200):
            deploy_progress_Op = CheckUAIDeployProgressApiOp(
                public_key=self.public_key,
                private_key=self.private_key,
                project_id=self.project_id,
                region=self.region,
                zone=self.zone,
                service_id=self.service_id,
                srv_version=rsp['SrvVersion']
            )
            deploy_process_succ, deploy_process_rsp = deploy_progress_Op.call_api()
            if not deploy_process_succ \
                    or deploy_process_rsp['Status'] == 'Error' \
                    or deploy_process_rsp['Status'] == 'Started' \
                    or deploy_process_rsp['Status'] == 'ToStart':
                break
            time.sleep(10)

        return succ, rsp
