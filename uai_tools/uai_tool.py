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

import argparse
from uai.utils.utils import param_filter
from uai.utils.logger import uai_logger

from uai.operation.tar.caffe_tar_op import UaiServiceCaffeTarOp
from uai.operation.tar.keras_tar_op import UaiServiceKerasTarOp
from uai.operation.tar.mxnet_tar_op import UaiServiceMxnetTarOp
from uai.operation.tar.tf_tar_op import UaiServiceTFTarOp

from uai.operation.pack.caffe_pack_op import UaiServiceCaffePackOp
from uai.operation.pack.keras_pack_op import UaiServiceKerasPackOp
from uai.operation.pack.mxnet_pack_op import UaiServiceMxnetPackOp
from uai.operation.pack.tf_pack_op import UaiServiceTFPackOp

from uai.operation.packdocker.caffe_packdocker_op import UaiServiceCaffeDockerPackOp
from uai.operation.packdocker.keras_packdocker_op import UaiServiceKerasDockerPackOp
from uai.operation.packdocker.mxnet_packdocker_op import UaiServiceMxnetDockerPackOp
from uai.operation.packdocker.tf_packdocker_op import UaiServiceTFDockerPackOp
from uai.operation.packdocker.self_define_packdokcer_op import UaiServiceSelfDockerPackOp

from uai.operation.create_uaiservice.create_uaiservice import UaiServiceCreateOp
from uai.operation.delete_uaiservice.delete_uaiservice import UaiServiceDeleteOp
from uai.operation.deploy_uaiservice.deploy_uaiservice import UaiServiceDeployByUfileOp
from uai.operation.deploy_uaiservice_docker.deploy_uaiservice_docker import UaiServiceDeployByDockerOp
from uai.operation.list_uaiservice.list_uaiservice import UaiServiceListServiceOp
from uai.operation.list_uaiversion.list_uaiversion import UaiServiceListSrvVersionOp
from uai.operation.modify_service_name.modify_service_name import UaiServiceModifyServiceNameOp
from uai.operation.modify_version_memo.modify_version_memo import UaiServiceModifySrvVersionMemoOp
from uai.operation.modify_version_weight.modify_version_weight import UaiServiceModifySrvVersionWeightOp
from uai.operation.modify_node_count.modify_node_count import UaiServiceModifySrvVersionNodeCountOp
from uai.operation.start_uaiservice.start_uaiservice import UaiServiceStartServiceOp
from uai.operation.stop_uaiservice.stop_uaiservice import UaiServiceStopServiceOp

def parse_args(subparser):
    create_parser = subparser.add_parser('create', help='Create UAI Service')
    delete_parser = subparser.add_parser('delete', help='Delete UAI Service')
    deploy_parser = subparser.add_parser('deploy', help='Deploy UAI Service by Ufile')
    deploy_docker_parser = subparser.add_parser('deploydocker', help='Deploy UAI Service by Docker')
    list_service_parser = subparser.add_parser('listservice', help='List UAI Service')
    list_verison_parser = subparser.add_parser('listversion', help='List UAI Service Version')
    modify_name_parser = subparser.add_parser('modifyname', help='Modify UAI Service Name')
    modify_memo_parser = subparser.add_parser('modifymemo', help='Modify UAI Service Memo')
    modify_weight_parser = subparser.add_parser('modifyweight', help='Modify UAI Service Version Weight')
    modify_node_count_parser = subparser.add_parser('modifynodecount', help='Set UAI Service Node Count')
    start_parser = subparser.add_parser('start', help='Start UAI Service')
    stop_parser = subparser.add_parser('stop', help='Stop UAI Service')

    tar_parser = subparser.add_parser('tar', help='Tar User Files for UAI Service')
    ai_tar_parser = tar_parser.add_subparsers(dest='ai_arch_type', help='ai_arch_type')
    caffe_tar_parser =  ai_tar_parser.add_parser('caffe', help='Tar Caffe User Files for UAI Service')
    keras_tar_parser = ai_tar_parser.add_parser('keras', help='Tar Keras User Files for UAI Service')
    mxnet_tar_parser = ai_tar_parser.add_parser('mxnet', help='Tar Mxnet User Files for UAI Service')
    tf_tar_parser = ai_tar_parser.add_parser('tf', help='Tar Tensorflow User Files for UAI Service')

    pack_parser = subparser.add_parser('pack', help='Pack User Files for UAI Service')
    ai_pack_parser = pack_parser.add_subparsers(dest='ai_arch_type', help='ai_arch_type')
    caffe_pack_parser =  ai_pack_parser.add_parser('caffe', help='Pack Caffe User Files for UAI Service')
    keras_pack_parser = ai_pack_parser.add_parser('keras', help='Pack Keras User Files for UAI Service')
    mxnet_pack_parser = ai_pack_parser.add_parser('mxnet', help='Pack MXNet User Files for UAI Service')
    tf_pack_parser = ai_pack_parser.add_parser('tf', help='Pack TF User Files for UAI Service')

    packdocker_parser = subparser.add_parser('packdocker', help='Packdocker User Files for UAI Service')
    ai_packdocker_parser = packdocker_parser.add_subparsers(dest='ai_arch_type', help='ai_arch_type')
    caffe_packdocker_parser =  ai_packdocker_parser.add_parser('caffe', help='Pack Docker of Caffe for UAI Service')
    keras_packdocker_parser = ai_packdocker_parser.add_parser('keras', help='Pack Docker of Keras for UAI Service')
    mxnet_packdocker_parser = ai_packdocker_parser.add_parser('mxnet', help='Pack Docker of MXNet for UAI Service')
    tf_packdocker_parser = ai_packdocker_parser.add_parser('tf', help='Pack Docker of TF for UAI Service')
    self_packdocker_parser = ai_packdocker_parser.add_parser('self', help='Pack Self-Defined Docker for UAI Service')

    create_op = UaiServiceCreateOp(create_parser)
    delete_op = UaiServiceDeleteOp(delete_parser)
    deploy_op = UaiServiceDeployByUfileOp(deploy_parser)
    docker_deploy_op = UaiServiceDeployByDockerOp(deploy_docker_parser)
    list_servie_op = UaiServiceListServiceOp(list_service_parser)
    list_version_op = UaiServiceListSrvVersionOp(list_verison_parser)
    modify_name_op = UaiServiceModifyServiceNameOp(modify_name_parser)
    modify_memo_op = UaiServiceModifySrvVersionMemoOp(modify_memo_parser)
    modify_weight_op = UaiServiceModifySrvVersionWeightOp(modify_weight_parser)
    modify_node_count_op = UaiServiceModifySrvVersionNodeCountOp(modify_node_count_parser)
    start_op = UaiServiceStartServiceOp(start_parser)
    stop_op = UaiServiceStopServiceOp(stop_parser)

    caffe_tar_op = UaiServiceCaffeTarOp(caffe_tar_parser)
    keras_tar_op = UaiServiceKerasTarOp(keras_tar_parser)
    mxnet_tar_op = UaiServiceMxnetTarOp(mxnet_tar_parser)
    tf_tar_op = UaiServiceTFTarOp(tf_tar_parser)

    caffe_pack_op = UaiServiceCaffePackOp(caffe_pack_parser)
    keras_pack_op = UaiServiceKerasPackOp(keras_pack_parser)
    mxnet_pack_op = UaiServiceMxnetPackOp(mxnet_pack_parser)
    tf_pack_op = UaiServiceTFPackOp(tf_pack_parser)

    caffe_packdocker_op = UaiServiceCaffeDockerPackOp(caffe_packdocker_parser)
    keras_packdocker_op = UaiServiceKerasDockerPackOp(keras_packdocker_parser)
    mxnet_packdocker_op = UaiServiceMxnetDockerPackOp(mxnet_packdocker_parser)
    tf_packdocker_op = UaiServiceTFDockerPackOp(tf_packdocker_parser)
    self_packdocker_op = UaiServiceSelfDockerPackOp(self_packdocker_parser)

    tar_op_dic = {
        "caffe": caffe_tar_op,
        "keras": keras_tar_op,
        "mxnet": mxnet_tar_op,
        "tf": tf_tar_op,
    }

    pack_op_dic = {
        "caffe": caffe_pack_op,
        "keras": keras_pack_op,
        "mxnet": mxnet_pack_op,
        "tf": tf_pack_op,
    }

    docker_pack_op_dic = {
        "caffe": caffe_packdocker_op,
        "keras": keras_packdocker_op,
        "mxnet": mxnet_packdocker_op,
        "tf": tf_packdocker_op,
        "self": self_packdocker_op,
    }

    cmd_op_dic = {
        "create": create_op,
        "delete": delete_op,
        "deploy": deploy_op,
        "deploydocker": docker_deploy_op,
        "listservice": list_servie_op,
        "listversion": list_version_op,
        "modifyname": modify_name_op,
        "modifymemo": modify_memo_op,
        "modifyweight": modify_weight_op,
        "modifynodecount": modify_node_count_op,
        "start": start_op,
        "stop": stop_op,

        "tar": tar_op_dic,
        "pack": pack_op_dic,
        "packdocker": docker_pack_op_dic,
    }

    return cmd_op_dic

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='UAI Inference Platform Commander',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    subparser = parser.add_subparsers(dest='commands', help='commands')

    cmd_op_dic = parse_args(subparser)
    cmd_args = param_filter(vars(parser.parse_args()))
    uai_logger.info("cmd_args: {0}".format(cmd_args))

    if cmd_args['commands'] == 'packdocker':
        cmd_op_dic.get('packdocker').get(cmd_args['ai_arch_type']).cmd_run(cmd_args)
    elif cmd_args['commands'] == 'pack':
        cmd_op_dic.get('pack').get(cmd_args['ai_arch_type']).cmd_run(cmd_args)
    elif cmd_args['commands'] == 'tar':
        cmd_op_dic.get('tar').get(cmd_args['ai_arch_type']).cmd_run(cmd_args)
    else:
        cmd_op_dic.get(cmd_args['commands']).cmd_run(cmd_args)
