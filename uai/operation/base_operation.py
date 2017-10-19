
class BaseUaiServiceOp(object):

    def __init__(self, parser):
        self.parser = parser
        self._add_args(self.parser)

    def _add_args(self, parser):
        args_parser = parser.add_argument_group('User-Params',
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
            '--project_id',
            type=str,
            required=False,
            help='the project id of ucloud, could be null')
        #add other params in subclasses#

    def _parse_args(self):
        self.public_key = self.params['public_key']
        self.private_key = self.params['private_key']
        self.project_id = self.params['project_id'] if 'project_id' in self.params else ''
        self.region = self.params['region'] if 'region' in self.params else ''
        self.zone =  self.params['zone'] if 'zone' in self.params else ''
        # add other params in subclasses#

    def cmd_run(self, params):
        self.params = params
        self._parse_args()
        pass
        # add other params in subclasses#