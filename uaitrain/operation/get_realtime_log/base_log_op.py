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
from uai.utils.logger import printConsoleOnlyError
from uaitrain.operation.base_op import BaseUAITrainOp
from uaitrain.api.get_train_job_running_log import GetUAITrainRunningLogApiOp
from uaitrain.api.get_train_job_list import GetUAITrainJobListApiOp


class BaseUAITrainGetRealtimeLogOp(BaseUAITrainOp):
    def __init__(self, parser):
        super(BaseUAITrainGetRealtimeLogOp, self).__init__(parser)
        printConsoleOnlyError()

    def _add_job_info_args(self, job_parser):
        info_parser = job_parser.add_argument_group(
            'Job Info Params', 'Job Infos')
        info_parser.add_argument(
            '--job_id',
            type=str,
            required=True,
            help='The <job_id> to query')
        info_parser.add_argument(
            '--log_topic_id',
            type=str,
            required=True,
            help='The <log_topic_id> to query')

    def _add_args(self):
        parser = self.parser.add_parser('log', help='Get realtime log of UAI Train Job')
        self.job_parser = parser
        self._add_account_args(parser)
        self._add_job_info_args(parser)

    def _parse_args(self, args):
        super(BaseUAITrainGetRealtimeLogOp, self)._parse_args(args)

        self.job_id = args['job_id']
        self.log_topic_id = args['log_topic_id']
        return True

    def _check_job_running(self):
        job_op = GetUAITrainJobListApiOp(
            pub_key=self.pub_key,
            priv_key=self.pri_key,
            job_id=self.job_id,
            project_id=self.project_id,
            region=self.region,
            zone=self.zone)

        succ, resp = job_op.call_api()
        if succ is False:
            print("Error get job status info. job {0} ".format(self.job_id))
            return False

        if resp['DataSet'][0]['Status'] in ['Done', 'Stopped', 'Deleted', 'Error']:
            return False
        return True

    def cmd_run(self, args):
        if self._parse_args(args) == False:
            return False

        while True:
            log_op = GetUAITrainRunningLogApiOp(
                pub_key=self.pub_key,
                priv_key=self.pri_key,
                job_id=self.job_id,
                log_topic_id=self.log_topic_id,
                project_id=self.project_id,
                region=self.region,
                zone=self.zone)

            succ, resp = log_op.call_api()
            if succ is False:
                uai_logger.warn("Error get realtime log info. job {0}, check your job_id, it may be not running.".format(self.job_id))
                time.sleep(10)
                continue
            result = resp['RunningLog'] if resp['RunningLog'] is not None else []
            for log in result:
                print (log)

            if self._check_job_running() is True:
                time.sleep(10)
            else:
                break
        return True
