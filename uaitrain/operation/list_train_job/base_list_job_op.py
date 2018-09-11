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

from uai.utils.logger import uai_logger
from uaitrain.operation.base_op import BaseUAITrainOp
from uaitrain.api.get_train_job_list import GetUAITrainJobListApiOp


class BaseUAITrainListTrainJobOp(BaseUAITrainOp):
    def __init__(self, parser):
        super(BaseUAITrainListTrainJobOp, self).__init__(parser)

    def _add_list_info_args(self, list_parser):
        info_parser = list_parser.add_argument_group(
            'Job Info Params', 'Job Infos')
        info_parser.add_argument(
            '--job_id',
            type=str,
            required=False,
            default='',
            help='Show the basic info of <job_id>')

        info_parser.add_argument(
            '--limit',
            type=int,
            required=False,
            default=10,
            help='Number of jobs show in this list')

    def _add_args(self):
        parser = self.parser.add_parser('list', help='List UAI Train Job')
        self.list_parser = parser
        self._add_account_args(parser)
        self._add_list_info_args(parser)

    def _parse_args(self, args):
        super(BaseUAITrainListTrainJobOp, self)._parse_args(args)

        self.job_id = args['job_id']
        self.limit = args['limit']
        self.offset = 1
        return True

    def _format_jobinfo(self, job):
        create_time = job['CreateTime']
        start_time = job['StartTime']
        end_time = job['EndTime']


        job_name = job['TrainJobName']
        job_id = job['TrainJobId']
        business_group = job['BusinessGroup']

        status = job['Status']

        print('JOB_NAME: {0}; JOB_ID: {1}; BUSINESS_ID: {2}; STATUS: {3}; CREATE_TIME: {4}; START_TIME: {5}; END_TIME: {6};'.format(
            job_name,
            job_id,
            business_group,
            status,
            datetime.datetime.fromtimestamp(create_time).strftime('%Y-%m-%d %H:%M:%S'),
            '' if start_time == 0 else datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S'),
            '' if end_time == 0 else datetime.datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')))

    def cmd_run(self, args):
        if self._parse_args(args) == False:
            return False

        job_op = GetUAITrainJobListApiOp(
            pub_key=self.pub_key,
            priv_key=self.pri_key,
            job_id=self.job_id,
            offset=self.offset,
            limit=self.limit,
            project_id=self.project_id,
            region=self.region,
            zone=self.zone)

        succ, resp = job_op.call_api()
        if succ is False:
            uai_logger.error("Error call list train jobs")
            return False

        result = resp['DataSet']
        for job in result:
            self._format_jobinfo(job)
        return True
