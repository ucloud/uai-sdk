import argparse
from ufile.operation.upload_single_op import UploadUfileSingleOp
from ufile.operation.download_single_op import DownloadUfileSingleOp
from ufile.operation.download_batch_op import DownloadUfileBatchOp
from ufile.operation.upload_batch_op import UploadUfileBatchOp

def parse_param(subparsers):
    download_batch_parser = subparsers.add_parser('download_batch', help='Batch download from ufile')
    download_batch_op = DownloadUfileBatchOp(download_batch_parser)

    upload_batch_parser = subparsers.add_parser('upload_batch', help='Batch upload to ufile')
    upload_batch_op = UploadUfileBatchOp(upload_batch_parser)

    download_single_parser = subparsers.add_parser('download_single', help='Download single file from ufile')
    download_single_op = DownloadUfileSingleOp(download_single_parser)

    upload_single_parser = subparsers.add_parser('upload_single', help='Upload single file to ufile')
    upload_single_op = UploadUfileSingleOp(upload_single_parser)

    cmd_op_dict = {
        'download_batch': download_batch_op,
        'upload_batch': upload_batch_op,
        'download_single': download_single_op,
        'upload_single': upload_single_op
    }

    return cmd_op_dict

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Ufile Commander',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers(dest='commands', help='commands')
    cmd_op_dict = parse_param(subparsers)

    params = vars(parser.parse_args())
    cmd_op_dict.get(params['commands']).cmd_run(params)
