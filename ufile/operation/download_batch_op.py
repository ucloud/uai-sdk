from ufile.api.ufile_api import DownloadUfileBatch
from ufile.operation.operation import Operation

class DownloadUfileBatchOp(Operation):

    def __init__(self, parser):
        super(DownloadUfileBatchOp, self).__init__(parser)

    def _add_args(self, parser):
        super(DownloadUfileBatchOp, self)._add_args(parser)
        args_parser = parser.add_argument_group('ufile-Params',
                                                'Uai Service Managment Parameters')
        args_parser.add_argument(
            '--public_key',
            type=str,
            required=True,
            help='the public key of the user')
        args_parser.add_argument(
            '--private_key',
            type=str,
            required=True,
            help='the private key of the user')
        args_parser.add_argument(
            '--bucket',
            type=str,
            required=True,
            help='the ufile bucket')
        args_parser.add_argument(
            '--prefix',
            type=str,
            required=True,
            help='the ufile prefix')
        args_parser.add_argument(
            '--local_dir',
            type=str,
            required=True,
            help='the dir that the ufile will be saved.')
        args_parser.add_argument(
            '--thread_num',
            type=int,
            required=False,
            default=8,
            help='the num of thread that will be start.')

    def _parse_args(self):
        super(DownloadUfileBatchOp, self)._parse_args()
        self.public_key = self.params['public_key']
        self.private_key = self.params['private_key']
        self.bucket = self.params['bucket']
        self.prefix = self.params['prefix']
        self.local_dir = self.params['local_dir']
        self.thread_num = self.params['thread_num']
        if self.thread_num < 0:
            raise RuntimeError("thread_num must be greater than 0. ")

    def cmd_run(self, params):
        super(DownloadUfileBatchOp, self).cmd_run(params)
        DownloadUfileBatch(self.public_key, self.private_key, self.bucket, self.prefix, self.local_dir, is_private=True, parall_num=self.thread_num)