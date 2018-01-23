import argparse
from uai.operation.create import UaiServiceCreateOp
from uai.operation.checkdeploy import UaiServiceCheckDeployOp
from uai.operation.deploy_docker import UaiServiceDeployOp
from uai.operation.deploy import UaiServiceDeployByUfileOp
from uai.operation.delete import UaiServiceDeleteOp
from uai.operation.checkbase import UaiServiceCheckBaseImgExistOp
from uai.operation.modifyweight import UaiServiceModifyWeightOp
from uai.operation.modifyname import UaiServiceModifyServiceNameOp
from uai.operation.listservice import UaiServiceListServiceOp
from uai.operation.listversion import UaiSrvVersionListOp
from uai.operation.start import UaiServiceStartOp
from uai.operation.stop import UaiServiceStopOp
from uai.operation.pack_docker.tf_pack_op import UaiServiceTFPackOp as UaiServiceTFPackOpDocker
from uai.operation.pack_docker.mxnet_pack_op import UaiServiceMxnetPackOp as UaiServiceMxnetPackOpDocker
from uai.operation.pack_docker.caffe_pack_op import UaiServiceCaffePackOp as UaiServiceCaffePackOpDocker
from uai.operation.pack_docker.keras_pack_op import UaiServiceKerasPackOp as UaiServiceKerasPackOpDocker
from uai.operation.pack.tf_pack_op import UaiServiceTFPackOp as UaiServiceTFPackOp
from uai.operation.pack.mxnet_pack_op import UaiServiceMxnetPackOp as UaiServiceMxnetPackOp
from uai.operation.pack.caffe_pack_op import UaiServiceCaffePackOp as UaiServiceCaffePackOp
from uai.operation.pack.keras_pack_op import UaiServiceKerasPackOp as UaiServiceKerasPackOp
from uai.operation.tar.keras_tar_op import UaiServiceKerasTarOp
from uai.operation.tar.mxnet_tar_op import UaiServiceMxnetTarOp
from uai.operation.tar.caffe_tar_op import UaiServiceCaffeTarOp
from uai.operation.tar.tf_tar_op import UaiServiceTFTarOp

def param_filter(params):
    res_params = {}
    for key in params:
        if params[key] is not None:
            res_params[key] = params[key]
    return res_params

def parse_param(subparsers):
    create_parser = subparsers.add_parser('create', help='Create new uai inference service task')
    create_op = UaiServiceCreateOp(create_parser)

    check_parser = subparsers.add_parser('checkprogress', help='check deploy progress')
    check_deploy_op = UaiServiceCheckDeployOp(check_parser)

    delete_parser = subparsers.add_parser('delete', help='Remove a whole inference service task or a version in a certian service task')
    delete_op = UaiServiceDeleteOp(delete_parser)

    stop_parser = subparsers.add_parser('stop', help='Stop the whole inference service task or a version in certian task')
    stop_op = UaiServiceStopOp(stop_parser)

    deploy_docker_parser = subparsers.add_parser('deploydocker', help='Deploy a uai inference service task by a certian uhub images')
    deploy_docker_op = UaiServiceDeployOp(deploy_docker_parser)

    deploy_parser = subparsers.add_parser('deploy', help='Deploy a uai inference service task by ufile')
    deploy_op = UaiServiceDeployByUfileOp(deploy_parser)

    start_parser = subparsers.add_parser('start', help='Start a version in a certian inference service task')
    start_op = UaiServiceStartOp(start_parser)

    listservice_parser = subparsers.add_parser('listservice', help='List serivces info, could specify one by service_id')
    listservice_op = UaiServiceListServiceOp(listservice_parser)

    listversion_parser = subparsers.add_parser('listversion', help='List versions info of a specified uai inference service task, could specify a certain version by service_version')
    listversion_op = UaiSrvVersionListOp(listversion_parser)

    modifyname_parser = subparsers.add_parser('modifyname', help='Modify the inference service task name')
    modifyname_op = UaiServiceModifyServiceNameOp(modifyname_parser)

    modifyweight_parser = subparsers.add_parser('modifyweight', help='Modify the inference service task weight for grayscale publishing')
    modifyweight_op = UaiServiceModifyWeightOp(modifyweight_parser)

    checkbase_parser = subparsers.add_parser('checkbase', help='Check base enviroment exists(os, python version, ai framework)')
    checkbase_op = UaiServiceCheckBaseImgExistOp(checkbase_parser)

    pack_docker_parser = subparsers.add_parser('packdocker', help='Pack local code into uhub')
    ai_frame_parse_docker = pack_docker_parser.add_subparsers(dest='ai_frame_type', help='ai_frame_type')
    tf_pack_docker_parser = ai_frame_parse_docker.add_parser('tf', help='pack_docker code of tensorflow ')
    tf_pack_docker_op = UaiServiceTFPackOpDocker(tf_pack_docker_parser)
    caffe_pack_docker_parser = ai_frame_parse_docker.add_parser('caffe', help='pack_docker code of of caffe')
    caffe_pack_docker_op = UaiServiceCaffePackOpDocker(caffe_pack_docker_parser)
    mxnet_pack_docker_parser = ai_frame_parse_docker.add_parser('mxnet', help='pack_docker code of mxnet')
    mxnet_pack_docker_op = UaiServiceMxnetPackOpDocker(mxnet_pack_docker_parser)
    keras_pack_docker_parser = ai_frame_parse_docker.add_parser('keras', help='pack_docker code of keras')
    keras_pack_docker_op = UaiServiceKerasPackOpDocker(keras_pack_docker_parser)
    pack_docker_op_dict = {
        'tf': tf_pack_docker_op,
        'caffe': caffe_pack_docker_op,
        'mxnet': mxnet_pack_docker_op,
        'keras': keras_pack_docker_op
    }

    pack_parser = subparsers.add_parser('pack', help='Pack local code into ufile')
    ai_frame_parse = pack_parser.add_subparsers(dest='ai_frame_type', help='ai_frame_type')
    tf_pack_parser = ai_frame_parse.add_parser('tf', help='pack code of tensorflow ')
    tf_pack_op = UaiServiceTFPackOp(tf_pack_parser)
    caffe_pack_parser = ai_frame_parse.add_parser('caffe', help='pack code of of caffe')
    caffe_pack_op = UaiServiceCaffePackOp(caffe_pack_parser)
    mxnet_pack_parser = ai_frame_parse.add_parser('mxnet', help='pack code of mxnet')
    mxnet_pack_op = UaiServiceMxnetPackOp(mxnet_pack_parser)
    keras_pack_parser = ai_frame_parse.add_parser('keras', help='pack code of keras')
    keras_pack_op = UaiServiceKerasPackOp(keras_pack_parser)
    pack_ufile_op_dict = {
        'tf': tf_pack_op,
        'caffe': caffe_pack_op,
        'mxnet': mxnet_pack_op,
        'keras': keras_pack_op
    }

    tar_parser = subparsers.add_parser('tar', help='tar local code file')
    ai_frame_parse = tar_parser.add_subparsers(dest='ai_frame_type', help='ai_frame_type')
    tf_tar_parser = ai_frame_parse.add_parser('tf', help='tar code of tensorflow ')
    tf_tar_op = UaiServiceTFTarOp(tf_tar_parser)
    caffe_tar_parser = ai_frame_parse.add_parser('caffe', help='tar code of of caffe')
    caffe_tar_op = UaiServiceCaffeTarOp(caffe_tar_parser)
    mxnet_tar_parser = ai_frame_parse.add_parser('mxnet', help='tar code of mxnet')
    mxnet_tar_op = UaiServiceMxnetTarOp(mxnet_tar_parser)
    keras_tar_parser = ai_frame_parse.add_parser('keras', help='tar code of keras')
    keras_tar_op = UaiServiceKerasTarOp(keras_tar_parser)
    tar_op_dict = {
        'tf': tf_tar_op,
        'caffe': caffe_tar_op,
        'mxnet': mxnet_tar_op,
        'keras': keras_tar_op
    }

    cmd_op_dict = {
        'create': create_op,
        'checkprogress': check_deploy_op,
        'delete': delete_op,
        'start': start_op,
        'stop': stop_op,
        'deploydocker': deploy_docker_op,
        'deploy': deploy_op,
        'listservice': listservice_op,
        'listversion': listversion_op,
        'modifyname': modifyname_op,
        'modifyweight': modifyweight_op,
        'checkbase': checkbase_op,
        'packdocker': pack_docker_op_dict,
        'pack': pack_ufile_op_dict,
        'tar': tar_op_dict
    }
    return cmd_op_dict

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='UAI Inference Platform Commander',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers(dest='commands', help='commands')
    cmd_op_dict = parse_param(subparsers)

    params = vars(parser.parse_args())
    print (params)
    params = param_filter(params)
    if params['commands'] == 'packdocker':
        print (cmd_op_dict.get('packdocker'))
        cmd_op_dict.get('packdocker').get(params['ai_frame_type']).cmd_run(params)
    elif params['commands'] == 'pack':
        cmd_op_dict.get('pack').get(params['ai_frame_type']).cmd_run(params)
    elif params['commands'] == 'tar':
        cmd_op_dict.get('tar').get(params['ai_frame_type']).cmd_run(params)
    else:
        succ, rsp = cmd_op_dict.get(params['commands']).cmd_run(params)
        print (rsp)