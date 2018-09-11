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
from uai.utils.logger import uai_logger
from uaitrain.operation.base_op import BaseUAITrainOp
from uaitrain.api.get_train_job_bill_info import GetUAITrainBillInfoApiOp


class BaseUAITrainListBillInfoOp(BaseUAITrainOp):
    def __init__(self, parser):
        super(BaseUAITrainListBillInfoOp, self).__init__(parser)

    def _add_list_info_args(self, list_parser):
        info_parser = list_parser.add_argument_group(
            'bill Info Params', 'bill Infos')
        info_parser.add_argument(
            '--begin_time',
            type=str,
            required=True,
            help='begin time')
        info_parser.add_argument(
            '--end_time',
            type=str,
            required=True,
            help='end time')
        info_parser.add_argument(
            '--limit',
            type=int,
            required=False,
            default=10,
            help='Number of jobs show in this list')

    def _add_args(self):
        parser = self.parser.add_parser('bill', help='Get bill info of UAI Train Job')
        self.list_parser = parser
        self._add_account_args(parser)
        self._add_list_info_args(parser)

    def _parse_args(self, args):
        super(BaseUAITrainListBillInfoOp, self)._parse_args(args)
        self.begin_time = self._datetime_timestamp(args['begin_time']) if 'begin_time' in args else ''
        self.end_time = self._datetime_timestamp(args['end_time']) if 'end_time' in args else ''

        self.limit = args['limit']
        self.offset = 1
        return True

    def _datetime_timestamp(self, dt):
        try:
            s = time.mktime(time.strptime(dt, '%Y-%m-%d %H:%M:%S'))
            return int(s)
        except Exception as e:
            raise RuntimeError('time format error, the time fomat should be %Y-%m-%d %H:%M:%S, such as 2017-03-28-6:53:40')

    def _format_billinfo(self, job):

        job_name = job['TrainJobName']
        job_id = job['TrainJobId']
        exec_time = job['ExecuteTime']
        total_price = float(job['TotalPrice'])/100

        print('JOB_NAME: {job_name}; JOB_ID: {job_id}; EXEC_TIME: {exec_time} s; TOTAL_PRICE: {total_price};'.format(
            job_name=job_name,
            job_id=job_id,
            exec_time=exec_time,
            total_price=total_price))

    def cmd_run(self, args):
        if self._parse_args(args) == False:
            return False

        bill_op = GetUAITrainBillInfoApiOp(
            pub_key=self.pub_key,
            priv_key=self.pri_key,
            beg_time=self.begin_time,
            end_time=self.end_time,
            offset=self.offset,
            limit=self.limit,
            project_id=self.project_id,
            region=self.region,
            zone=self.zone)

        succ, resp = bill_op.call_api()
        if succ is False:
            uai_logger.error("Error call list bill info")
            return False

        print('Total job num: {0}, Total exec time: {1} s, Total price: {2} yuan;'.format(
            resp['TotalCount'],
            resp['TotalExecuteTime'],
            float(resp['TotalPrice'])/100))

        result = resp['DataSet']
        for job_bill in result:
            self._format_billinfo(job_bill)
        return True
