from ufile.api.ufile_api import UploadUfileSingle
from ufile.operation.operation import Operation

class UploadUfileSingleOp(Operation):

    def __init__(self, parser):
        super(UploadUfileSingleOp, self).__init__(parser)

    def _add_args(self, parser):
        super(UploadUfileSingleOp, self)._add_args(parser)
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
            '--local_path',
            type=str,
            required=True,
            help='the path of local file that will be upload to ufile.')

    def _parse_args(self):
        super(UploadUfileSingleOp, self)._parse_args()
        self.public_key = self.params['public_key']
        self.private_key = self.params['private_key']
        self.bucket = self.params['bucket']
        self.prefix = self.params['prefix']
        self.local_path = self.params['local_path']

    def cmd_run(self, params):
        super(UploadUfileSingleOp, self).cmd_run(params)
        UploadUfileSingle(self.public_key, self.private_key, self.bucket, self.prefix, self.local_path)