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
from uaitrain.operation.base_op import BaseUAITrainOp
from uaitrain.api.remove_train_job import RemoveUAITrainJobApiOp


class BaseUAITrainDeleteTrainJobOp(BaseUAITrainOp):
    def __init__(self, parser):
        super(BaseUAITrainDeleteTrainJobOp, self).__init__(parser)

    def _add_delete_info_args(self, delete_parser):
        info_parser = delete_parser.add_argument_group(
            'Job Info Params', 'Job Infos')
        info_parser.add_argument(
            '--job_id',
            type=str,
            required=True,
            help='The <job_id> to delete')

    def _add_args(self):
        parser = self.parser.add_parser('delete', help='Delete UAI Train Job')
        self.delete_parser = parser
        self._add_account_args(parser)
        self._add_delete_info_args(parser)

    def _parse_args(self, args):
        super(BaseUAITrainDeleteTrainJobOp, self)._parse_args(args)
        self.job_id = args['job_id']
        return True

    def cmd_run(self, args):
        if self._parse_args(args) == False:
            return False

        delete_op = RemoveUAITrainJobApiOp(
            pub_key=self.pub_key,
            priv_key=self.pri_key,
            job_id=self.job_id,
            project_id=self.project_id,
            region=self.region,
            zone=self.zone)

        succ, resp = delete_op.call_api()
        if succ is False:
            print("Error delete job {0}, err msg: {1}".format(self.job_id, resp['Message']))
            return False

        print("Success delete job {0}".format(self.job_id))
        return True
