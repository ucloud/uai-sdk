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

import sys
import os
import argparse
import json
import subprocess

from uai.utils.logger import uai_logger
from uaitrain.operation.base_op import BaseUAITrainOp
from uaitrain.api.get_train_job_running_info import GetUAITrainRunningInfoOp

class BaseUAITrainRunningJobInfoOp(BaseUAITrainOp):
    def __init__(self, parser):
        super(BaseUAITrainRunningJobInfoOp, self).__init__(parser)

    def _add_job_info_args(self, info_parser):
        job_info_parser = info_parser.add_argument_group(
            'Job Info Params', 'Job Infos')
        job_info_parser.add_argument(
            '--job_id',
            type=str,
            required=True,
            help='The <job_id> to show Job Info')

    def _add_args(self):
        parser = self.parser.add_parser('info', help='Show UAI Train Job Info')
        self.info_parser = parser
        self._add_account_args(parser)
        self._add_job_info_args(parser)

    def _parse_args(self, args):
        super(BaseUAITrainRunningJobInfoOp, self)._parse_args(args)

        self.job_id = args['job_id']
        return True

    def _format_info(self, job_id, resp):
        exec_time = resp['ExecTime']
        cost = resp['TotalPrice']

        print('JOB_ID: {0}; ExecTime: {1} secs; Total Cost: {2}'.format(
            job_id,
            exec_time,
            float(cost) / 100))

    def cmd_run(self, args):
        if self._parse_args(args) == False:
            return False

        info_op = GetUAITrainRunningInfoOp(
            pub_key=self.pub_key,
            priv_key=self.pri_key,
            job_id=self.job_id,
            project_id=self.project_id,
            region=self.region,
            zone=self.zone)

        succ, resp = info_op.call_api()
        if succ is False:
            print("Error get job info of {0}, check your job_id".format(self.job_id))
            return False

        self._format_info(self.job_id, resp)
