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
from uai.utils.utils import parse_unrequired_args
from uai.utils.databackend_utils import concat_ufs_path
from uai.utils.databackend_utils import get_data_backend_name

from uaitrain.operation.base_op import BaseUAITrainOp
from uaitrain.api.create_train_job import CreateUAITrainJobApiOp
from uaitrain.api.get_train_available_resource import GetUAITrainAvailableResourceApiOp
from uaitrain.api.get_train_available_backend import GetUAITrainAvailableBackendApiOp
from uaitrain.api.get_train_available_dist_aiframe import GetUAITrainAvailableDistAIFrameApiOp
from uaitrain.api.get_train_available_train_mode import GetUAITrainAvailableTrainModeApiOp


class BaseUAITrainCreateTrainJobOp(BaseUAITrainOp):
    def __init__(self, parser):
        super(BaseUAITrainCreateTrainJobOp, self).__init__(parser)

    def _add_job_info_args(self, parser):
        job_parser = parser.add_argument_group(
            'Job Info Params', 'Parameters of train job info'
        )
        job_parser.add_argument(
            '--job_name',
            type=str,
            required=True,
            help='Name of created train job'
        )
        job_parser.add_argument(
            '--job_memo',
            type=str,
            required=False,
            help='Memo of created train job'
        )
        job_parser.add_argument(
            '--business_group',
            type=str,
            required=False,
            default='default',
            help='Business group of created train job'
        )
        job_parser.add_argument(
            '--max_exec_time',
            type=int,
            required=True,
            help='Max execute time of created train job, unit: hour'
        )
        job_parser.add_argument(
            '--dist_ai_frame',
            type=str,
            required=False,
            help='Dist ai framework name of created train job, could not be nil if train mode is "Distributed"'
        )

    def _add_node_info_args(self, parser):
        node_parser = parser.add_argument_group(
            'Node Info Params', 'Parameters of node info'
        )
        node_parser.add_argument(
            '--node_type',
            type=str,
            required=True,
            help='Name of work server node, e.g. 1-P40, 2-P40, 4-P40...'
        )
        node_parser.add_argument(
            '--node_num',
            type=int,
            default=1,
            required=False,
            help='Amount of work server node, default is 1'
        )


    def _add_execute_info_args(self, parser):
        execute_parser = parser.add_argument_group(
            'Execute Info Params', 'Parameters of execute info'
        )
        # docker dep info
        execute_parser.add_argument(
            '--code_uhub_path',
            type=str,
            required=True,
            help='Full docker image path of created train job, including docker registry, image name, image tag...'
        )
        execute_parser.add_argument(
            '--docker_cmd',
            type=str,
            required=True,
            help='Docker cmd for running train job'
        )
        execute_parser.add_argument(
            '--data_ufile_path',
            type=str,
            required=False,
            help='The ufile path to store the data'
        )
        execute_parser.add_argument(
            '--output_ufile_path',
            type=str,
            required=False,
            help='The ufile path to store the output'
        )
        execute_parser.add_argument(
            '--data_ufs_path',
            type=str,
            required=False,
            help='The ufs path to store the data'
        )
        execute_parser.add_argument(
            '--data_ufs_mount_point',
            type=str,
            required=False,
            help='The ufs mount point for the data'
        )
        execute_parser.add_argument(
            '--output_ufs_path',
            type=str,
            required=False,
            help='The ufs path to store the output'
        )
        execute_parser.add_argument(
            '--output_ufs_mount_point',
            type=str,
            required=False,
            help='The ufs mount point for the output'
        )

    def _parse_job_info_args(self, args):
        self.trainjob_name = args['job_name']
        self.trainjob_memo = parse_unrequired_args('job_memo', args)
        self.business_group = parse_unrequired_args('business_group', args)
        self.max_exec_time = args['max_exec_time']
        if self.max_exec_time <= 0:
            raise ValueError("Parameter max_exec_time should be larger than 0")
        self.dist_ai_frame = parse_unrequired_args('dist_ai_frame', args)

    def _parse_node_info_args(self, args):
        self.work_node = args['node_type']
        self.work_amount = args['node_num']
        if self.work_amount <= 0:
            raise ValueError("Parameter node_num should be larger than 0")

        if self.work_amount > 1:
            self.train_mode = 'Distributed'
        else:
            self.train_mode = 'StandAlone'

    def _parse_execute_info_args(self, args):
        self.code_uhub_path = args['code_uhub_path']
        self.docker_cmd = args['docker_cmd']
        if args['data_ufile_path'] is not None:
            self.input_path = args['data_ufile_path']
        elif args['data_ufs_path'] is not None:
            if args['data_ufs_mount_point'] is not None:
                ufs_path = args['data_ufs_path']
                ufs_mount = args['data_ufs_mount_point']
                self.input_path = concat_ufs_path(ufs_path, ufs_mount)
            else:
                raise ValueError("Need data_ufs_mount_point")
        else:
            raise ValueError("Need either data_ufile_path or data_ufs_path")
        if args['output_ufile_path'] is not None:
            self.output_path = args['output_ufile_path']
        elif args['output_ufs_path'] is not None:
            if args['output_ufs_mount_point'] is not None:
                ufs_path = args['output_ufs_path']
                ufs_mount = args['output_ufs_mount_point']
                self.output_path = concat_ufs_path(ufs_path, ufs_mount)
            else:
                raise ValueError("Need output_ufs_mount_point")
        else:
            raise ValueError("Need either output_ufile_path or output_ufs_path")

    def _add_args(self):
        parser = self.parser.add_parser('create', help='Create UAI Train Job')
        self._add_account_args(parser)
        self._add_job_info_args(parser)
        self._add_node_info_args(parser)
        self._add_execute_info_args(parser)

    def _parse_args(self, args):
        self._parse_account_args(args)
        self._parse_job_info_args(args)
        self._parse_node_info_args(args)
        self._parse_execute_info_args(args)

    def cmd_run(self, args):
        self._parse_args(args)

        train_mode_id = self._get_train_mode_id()
        work_node_id = self._get_node_id(train_mode_id)
        dist_ai_frame_id = self._get_dist_ai_frame_id(train_mode_id)
        input_backend_id = self._get_data_backend_id(train_mode_id, self.input_path)
        output_backend_id = self._get_data_backend_id(train_mode_id, self.output_path)

        create_op = CreateUAITrainJobApiOp(
            pub_key=self.pub_key,
            priv_key=self.pri_key,
            job_name=self.trainjob_name,
            work_node=work_node_id,
            image_path=self.code_uhub_path,
            input_path=self.input_path,
            input_backend=input_backend_id,
            output_path=self.output_path,
            output_backend=output_backend_id,
            docker_cmd=self.docker_cmd,
            max_exec_time=self.max_exec_time,
            train_mode=train_mode_id,
            work_amount=self.work_amount,
            dist_ai_frame=dist_ai_frame_id,
            business_group=self.business_group,
            job_memo=self.trainjob_memo,
            project_id=self.project_id,
            region=self.region,
            zone=self.zone)

        succ, rsp = create_op.call_api()
        if not succ:
            raise RuntimeError("Call CreateUAITrainJob fail, Err message:[{0}]{1}".format(rsp['RetCode'], rsp['Message']))
        print('Newly created train job is: {0}'.format(rsp['TrainJobId']))
        return succ, rsp

    # relations
    def _get_train_mode_id(self):
        train_mode_api = GetUAITrainAvailableTrainModeApiOp(self.pub_key, self.pri_key)
        succ, rsp = train_mode_api.call_api()
        if not succ:
            raise RuntimeError("Call GetUAITrainAvailableTrainMode fail, Err message:[{0}]{1}".format(rsp['Retcode'], rsp['Message']))
        for available_mode in rsp['DataItem']:
            if available_mode['TrainModeName'].lower() == self.train_mode.lower():
                return available_mode['TrainModeId']
        raise ValueError("Current train mode {0} is not supported".format(self.train_mode))

    def _get_node_id(self, train_mode_id):
        node_api = GetUAITrainAvailableResourceApiOp(train_mode_id, self.pub_key, self.pri_key)
        succ, rsp = node_api.call_api()
        if not succ:
            raise RuntimeError("Call GetUAITrainAvailableResource fail, Err message:[{0}]{1}".format(rsp['Retcode'], rsp['Message']))
        nodeinfo = self.work_node.lower().split('-')
        acc_amount, acc_name = int(nodeinfo[0]), nodeinfo[1]
        # available_nodes = rsp['DataSet']
        for available_node in rsp['DataSet']:
            if acc_name == available_node['AcceleratorVersion'].lower() and acc_amount == available_node['AcceleratorAmount']:
                return available_node['NodeId']
        raise ValueError("Current node server {0} is not supported".format(self.work_node))

    def _get_dist_ai_frame_id(self, train_mode_id):
        if self.dist_ai_frame == "":
            return 0
        aiframe_api = GetUAITrainAvailableDistAIFrameApiOp(train_mode_id, self.pub_key, self.pri_key)
        succ, rsp = aiframe_api.call_api()
        if not succ:
            raise RuntimeError("Call GetUAITrainAvailableDistAIFrame fail, Err message:[{0}]{1}".format(rsp['Retcode'], rsp['Message']))
        for available_aiframe in rsp['DataItem']:
            if available_aiframe['DistAIFrameName'].lower() == self.dist_ai_frame.lower():
                return available_aiframe['DistAIFrameId']
        raise ValueError("Current data backend {0} is not supported".format(self.dist_ai_frame))

    def _get_data_backend_id(self, train_mode_id, data_path):
        uai_logger.debug("Data_path: {0}".format(data_path))
        data_backend = get_data_backend_name(data_path)
        uai_logger.debug("Data_backend_name: {0}".format(data_backend))
        backend_api = GetUAITrainAvailableBackendApiOp(train_mode_id, self.pub_key, self.pri_key)
        succ, rsp = backend_api.call_api()
        if not succ:
            raise RuntimeError("Call GetUAITrainAvailableBackend fail, Err message:[{0}]{1}".format(rsp['Retcode'], rsp['Message']))
        for available_backend in rsp['DataItem']:
            if available_backend['DataBackendName'].lower() == data_backend.lower():
                uai_logger.debug("Data_backend_id: {0}".format(available_backend['DataBackendId']))
                return available_backend['DataBackendId']
        raise ValueError("Current data backend {0} is not supported".format(data_backend))
