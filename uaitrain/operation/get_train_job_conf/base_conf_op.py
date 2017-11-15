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

import datetime

from uai.utils.utils import GATEWAY_DEFAULT
from uai.utils.logger import uai_logger
from uaitrain.operation.base_op import BaseUAITrainOp
from uaitrain.api.get_train_job_list import GetUAITrainJobListOp
from uaitrain.api.get_train_job_running_info import GetUAITrainRunningInfoOp

class BaseUAITrainTrainJobConfOp(BaseUAITrainOp):
    def __init__(self, parser):
        super(BaseUAITrainTrainJobConfOp, self).__init__(parser)

    def _add_list_info_args(self, list_parser):
        info_parser = list_parser.add_argument_group(
            'Job Info Params', 'Job Infos')
        info_parser.add_argument(
            '--job_id',
            type=str,
            required=True,
            default='',
            help='Show the config info of <job_id>')

    def _add_args(self):
        parser = self.parser.add_parser('conf', help='Get conf of UAI Train Job')
        self.list_parser = parser
        self._add_account_args(parser)
        self._add_list_info_args(parser)

    def _parse_args(self, args):
        super(BaseUAITrainTrainJobConfOp, self)._parse_args(args)

        self.job_id = args['job_id']
        return True

    def _get_job_bill(self):
        op = GetUAITrainRunningInfoOp(pub_key=self.pub_key,
                                     priv_key=self.pri_key,
                                     project_id=self.project_id,
                                     job_id=self.job_id)

        succ, res = op.call_api()
        if succ != True:
            print ('Error get job info, job id: {0}'.format(self.job_id))
            return '', ''
        return res['ExecTime'], float(res['TotalPrice'])/100

    def _format_jobinfo(self, job):

        job_name = job['TrainJobName']
        job_id = job['TrainJobId']
        code_img = job['CodeUhubPath']
        data_path = job["DataUfilePath"]
        out_path = job['OutputUfilePath']
        cmd = job['DockerCmd']
        status = job['Status']
        exec_time, price = self._get_job_bill()

        print ('-----------------------------------------------------')
        print(
            '''
            JOB_NAME: {job_name} 
            JOB_ID: {job_id}
            CODE_IMAGE: {code_img}
            DATA_PATH: {data_path}
            OUT_PATH: {out_path}
            CMD: {cmd}
            STATUS: {status}
            EXEC_TIME: {exec_time}s
            PRICE: {price}'''.format(
            job_name=job_name,
            job_id=job_id,
            code_img=code_img,
            data_path=data_path,
            out_path=out_path,
            cmd=cmd,
            status=status,
            exec_time=exec_time,
            price=price))
        print ('-----------------------------------------------------')

    def cmd_run(self, args):
        if self._parse_args(args) == False:
            return False

        create_op = GetUAITrainJobListOp(
            pub_key=self.pub_key,
            priv_key=self.pri_key,
            job_id=self.job_id,
            project_id=self.project_id,
            region=self.region,
            zone=self.zone)

        succ, resp = create_op.call_api()
        if succ is False:
            uai_logger.error("Error call list train jobs")
            return False
        if resp['TotalCount'] == 0:
            uai_logger.error("can't get the config of this job id: {0}, please check your job id".format(self.job_id))
            return False

        job = resp['DataSet'][0]
        self._format_jobinfo(job)
        return True
