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
from uaitrain.api.get_train_tensorboard_url import GetUAITrainTensorboardUrlOp
from uaitrain.api.get_train_job_list import GetUAITrainJobListOp

class BaseUAITrainGetTensorBoardUrlOp(BaseUAITrainOp):
    def __init__(self, parser):
        super(BaseUAITrainGetTensorBoardUrlOp, self).__init__(parser)

    def _add_job_info_args(self, job_parser):
        info_parser = job_parser.add_argument_group(
            'Job Info Params', 'Job Infos')
        info_parser.add_argument(
            '--job_id',
            type=str,
            required=True,
            help='The <job_id> to query')

    def _add_args(self):
        parser = self.parser.add_parser('url', help='tensorboard url of UAI Train Job')
        self.job_parser = parser
        self._add_account_args(parser)
        self._add_job_info_args(parser)

    def _parse_args(self, args):
        super(BaseUAITrainGetTensorBoardUrlOp, self)._parse_args(args)

        self.job_id = args['job_id']
        return True

    def _check_job_running(self):
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

        status = resp['DataSet'][0]['Status']
        if status == 'Doing':
            return True
        else:
            return False

    def cmd_run(self, args):
        if self._parse_args(args) == False:
            return False

        if self._check_job_running() is False:
            print ('The job is not running or not exist. job id: {0}'.format(self.job_id))
            return False

        tensor_op = GetUAITrainTensorboardUrlOp(
            pub_key=self.pub_key,
            priv_key=self.pri_key,
            job_id=self.job_id,
            project_id=self.project_id,
            region=self.region,
            zone=self.zone)

        succ, resp = tensor_op.call_api()
        if succ is False:
            print("Error get tensorboard url info. job {0}, check your job_id, it may be not running.".format(self.job_id))
            return False

        print("Success. job_id: {0}, TensorBoard URL: {1}".format(self.job_id, resp['TensorboardURL']))
        return True