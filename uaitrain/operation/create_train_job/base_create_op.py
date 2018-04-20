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

from uai.utils.utils import GATEWAY_DEFAULT
from uaitrain.operation.base_op import BaseUAITrainOp
from uaitrain.api.create_train_job import CreateUAITrainJobOp
from uaitrain.api.get_train_available_resource import GetUAITrainAvailableResourceOp
from uaitrain.api.get_env_pkg import GetUAITrainEnvPkgAPIOp

class BaseUAITrainCreateTrainJobOp(BaseUAITrainOp):
    def __init__(self, parser):
        super(BaseUAITrainCreateTrainJobOp, self).__init__(parser)

    def _add_create_info_args(self, create_parser):
        info_parser = create_parser.add_argument_group(
            'Job Info Params', 'Job Infos')
        info_parser.add_argument(
            '--job_name',
            type=str,
            required=True,
            help='The train job name')
        info_parser.add_argument(
            '--job_memo',
            type=str,
            required=False,
            default=GATEWAY_DEFAULT,
            help='The train job memo')
        info_parser.add_argument(
            '--business_group',
            type=str,
            required=False,
            default=GATEWAY_DEFAULT,
            help='The train business group train job belong to')

    def _add_create_config_args(self, create_parser):
        node_parser = create_parser.add_argument_group(
            'Job Executor Params', 'Job Executor information')
        node_parser.add_argument(
            '--node_type',
            type=str,
            required=True,
            help='The training node used: e.g., 1-P40')

    def _add_create_job_args(self, create_parser):
        run_parser = create_parser.add_argument_group(
            'Job Runninng Params', 'Job Execution infos')
        run_parser.add_argument(
            '--code_uhub_path',
            type=str,
            required=True,
            help='The uhub docker path of training code')
        run_parser.add_argument(
            '--docker_cmd',
            type=str,
            required=True,
            help='The running python cmd inside docker')
        run_parser.add_argument(
            '--max_exec_time',
            type=int,
            required=True,
            help='The maximun running time in hours, should larger than 6 hours')

    def _add_create_ufile_args(self, create_parser):
        ufile_parser = create_parser.add_argument_group(
            'Ufile Params', 'Data/Output Stored in Ufile')
 
        ufile_parser.add_argument(
            '--data_ufile_path',
            type=str,
            required=False,
            help='The ufile path store the data')
        ufile_parser.add_argument(
            '--output_ufile_path',
            type=str,
            required=False,
            help='The ufile path store the output')

    def _add_create_ufs_args(self, create_parser):
        ufs_parser = create_parser.add_argument_group(
            'UFS Params', 'Data/Output Stored in UFS')
 
        ufs_parser.add_argument(
            '--data_ufs_path',
            type=str,
            required=False,
            help='The ufs path storing the data')
        ufs_parser.add_argument(
            '--data_ufs_mount_point',
            type=str,
            required=False,
            help='The ufs mount point for the data')
        ufs_parser.add_argument(
            '--output_ufs_path',
            type=str,
            required=False,
            help='The ufs path storing the output')
        ufs_parser.add_argument(
            '--output_ufs_mount_point',
            type=str,
            required=False,
            help='The ufs mount point for the output')

    def _add_create_dist_args(self, create_parser):
        dist_parser = create_parser.add_argument_group(
            'Dist-train Params', '')

        dist_parser.add_argument(
            '--dist_ai_frame',
            type=str,
            required=False,
            help='The AI framework for dist-train.(eg. tensorflow, mxnet). if you do not use dist-train, ignore it')
        dist_parser.add_argument(
            '--node_num',
            type=int,
            default=1,
            required=False,
            help='The num of node for dist-train. if you do not use dist-train, ignore it')

    def _add_args(self):
        parser = self.parser.add_parser('create', help='Create UAI Train Job')
        self.create_parser = parser
        self._add_account_args(parser)
        self._add_create_info_args(parser)
        self._add_create_config_args(parser)
        self._add_create_job_args(parser)
        self._add_create_ufile_args(parser)
        self._add_create_ufs_args(parser)
        self._add_create_dist_args(parser)

    def _parse_args(self, args):
        super(BaseUAITrainCreateTrainJobOp, self)._parse_args(args)

        #info
        self.job_name = args['job_name']
        self.job_memo = args['job_memo'] if 'job_memo' in args else ""
        self.business_group = args['business_group'] if 'business_group' in args else ""

        #config
        self.node_type = args['node_type']

        #job
        self.code_uhub_path = args['code_uhub_path']
        self.docker_cmd = args['docker_cmd']
        self.max_exec_time = args['max_exec_time']

        #data
        if 'data_ufile_path' in args:
            self.data_path = args['data_ufile_path']
        elif 'data_ufs_path' in args:
            if 'data_ufs_mount_point' in args:
                ufs_path = args['data_ufs_path']
                ufs_mount = args['data_ufs_mount_point']
                self.data_path = concat_ufs_path(ufs_path, ufs_mount)
            else:
                raise RuntimeError("Need data_ufs_mount_point")
        else:
            raise RuntimeError("Need either data_ufile_path or data_ufs_path")

        #output
        if 'output_ufile_path' in args:
            self.output_path = args['output_ufile_path']
        elif 'output_ufs_path' in args:
            if 'output_ufs_mount_point' in args:
                ufs_path = args['output_ufs_path']
                ufs_mount = args['output_ufs_mount_point']
                self.output_path = concat_ufs_path(ufs_path, ufs_mount)
            else:
                raise RuntimeError("Need output_ufs_mount_point")
        else:
            raise RuntimeError("Need either output_ufile_path or output_ufs_path")

        #dist
        self.dist_ai_frame = args['dist_ai_frame'] if 'dist_ai_frame' in args else ""
        self.worker_num = args['node_num']

        if self.dist_ai_frame != "" and self.worker_num <= 1:
            raise RuntimeError("The num of node for dist-train {0} should be greater 1, please check param node_num".format(self.dist_ai_frame))
        return True

    def _check_res(self):
        get_train_res_op = GetUAITrainAvailableResourceOp(self.pub_key,
            self.pri_key)
        succ, result = get_train_res_op.call_api()
        if succ is False:
            raise RuntimeError("Error get Training Resouce Type")

        nodeStr = self.node_type.lower().split("-")
        accV = nodeStr[1]
        accNum = nodeStr[0]
        data_set = result['DataSet']
        for data in data_set:
            if accV == data['AcceleratorVersion'].lower() and int(accNum) == int(data['AcceleratorAmount']):
                return data['NodeId']

        print("Required Type {0} not exist", self.node_type)
        print("Now only support {0}", result['DataSet'])
        RuntimeError('Unsupported node_type')
        return -1

    def _get_dist_ai_frame_id(self):
        pkgtype = "DistAIFrame"
        api_op = GetUAITrainEnvPkgAPIOp(self.pub_key,
                                        self.pri_key,
                                        pkgtype,
                                        self.project_id,
                                        self.region,
                                        self.zone)
        succ, result = api_op.call_api()

        if succ is False:
            raise RuntimeError("Error get {0} info from server".format(pkgtype))

        for avpkg in result['PkgSet']:
            if avpkg["PkgName"] == self.dist_ai_frame:
                    return avpkg["PkgId"]

        ai_frame_set = [avpkg["PkgId"] for avpkg in result['PkgSet']]

        print("Required Dist-frame {0} not exist", self.dist_ai_frame)
        print("Now only support {0}", ai_frame_set)
        raise RuntimeError("Some {0} package is not supported: {1}".format(pkgtype, self.dist_ai_frame))

    def cmd_run(self, args):
        if self._parse_args(args) == False:
            return False

        node_id = self._check_res()
        if node_id < 0:
            return False

        ai_frame_id = self._get_dist_ai_frame_id() if self.dist_ai_frame != '' else ''

        create_op = CreateUAITrainJobOp(
            pub_key=self.pub_key,
            priv_key=self.pri_key,
            job_name=self.job_name,
            work_id=node_id,
            code_uhub_path=self.code_uhub_path,
            data_ufile_path=self.data_path,
            out_ufile_path=self.output_path,
            docker_cmd=self.docker_cmd,
            max_exec_time=self.max_exec_time,
            work_num=self.worker_num,
            dist_ai_frame=ai_frame_id,
            business_group=self.business_group,
            job_memo=self.job_memo,
            project_id=self.project_id,
            region=self.region,
            zone=self.zone)

        succ, resp = create_op.call_api()
        if succ is False:
            print("Error call create train job")
            return False

        print('Your Job ID is: {0}'.format(resp['TrainJobId']))

