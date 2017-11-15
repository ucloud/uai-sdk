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

from uai.utils.logger import uai_logger
from uaitrain.operation.base_op import BaseUAITrainOp
from uaitrain.api.modify_train_job_name import ModifyUAITrainJobNameOp

class BaseUAITrainRenameTrainJobOp(BaseUAITrainOp):
    def __init__(self, parser):
        super(BaseUAITrainRenameTrainJobOp, self).__init__(parser)

    def _add_rename_info_args(self, rename_parser):
        info_parser = rename_parser.add_argument_group(
            'Job Info Params', 'Job Infos')
        info_parser.add_argument(
            '--job_id',
            type=str,
            required=True,
            help='The <job_id> to rename')
        info_parser.add_argument(
            '--job_name',
            type=str,
            required=True,
            help='the uai train name')

    def _add_args(self):
        parser = self.parser.add_parser('rename', help='Rename UAI Train Job')
        self.stop_parser = parser
        self._add_account_args(parser)
        self._add_rename_info_args(parser)

    def _parse_args(self, args):
        super(BaseUAITrainRenameTrainJobOp, self)._parse_args(args)

        self.job_id = args['job_id']
        self.job_name = args['job_name']
        return True


    def cmd_run(self, args):
        if self._parse_args(args) == False:
            return False

        create_op = ModifyUAITrainJobNameOp(
            pub_key=self.pub_key,
            priv_key=self.pri_key,
            job_id=self.job_id,
            job_name=self.job_name,
            project_id=self.project_id,
            region=self.region,
            zone=self.zone)

        succ, resp = create_op.call_api()
        if succ is False:
            print("Error call rename train job {0}".format(self.job_id))
            return False

        print("Success rename job {0}".format(self.job_id))
