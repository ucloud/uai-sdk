from uai.operation.base_operation import BaseUaiServiceOp
from uai.api.get_uai_available_env_pkg import GetUAIAvailableEnvPkgOp


class UaiServiceGetAvailableEnvPkgOp(BaseUaiServiceOp):
    def __init__(self, parser):
        super(UaiServiceGetAvailableEnvPkgOp, self).__init__(parser)

    def _add_args(self, parser):
        super(UaiServiceGetAvailableEnvPkgOp, self)._add_args(parser)
        args_parser = parser.add_argument_group()
        args_parser.add_argument(
            '--pkg_type',
            type=str,
            choices=['OS', 'Python', 'AIFrame'],
            required=False,
            help='enviroment pakcage type (choose in OS, Python, AIFrame)')
         # add other params in subclasses#

    def _parse_args(self):
        super(UaiServiceGetAvailableEnvPkgOp, self)._parse_args()
        self.pkg_type = self.params['pkg_type'] if 'pkg_type' in self.params else ''
        # add other params in subclasses#

    def cmd_run(self, params):
        super(UaiServiceGetAvailableEnvPkgOp, self).cmd_run(params)
        getEnvOp = GetUAIAvailableEnvPkgOp(public_key=self.public_key,
                                      private_key=self.private_key,
                                      project_id=self.project_id,
                                      region=self.region,
                                      zone=self.zone,
                                      pkg_type=self.pkg_type)
        succ, rsp = getEnvOp.call_api()
        return succ, rsp
