from uai.operation.base_operation import BaseUaiServiceOp
from uai.api.get_uai_srv_available_resource import GetUAISrvAvailableResource


class UaiServiceGetUAISrvAvailableResourceOp(BaseUaiServiceOp):
    def __init__(self, parser):
        super(UaiServiceGetUAISrvAvailableResourceOp, self).__init__(parser)

    def _add_args(self, parser):
        super(UaiServiceGetUAISrvAvailableResourceOp, self)._add_args(parser)
         # add other params in subclasses#

    def _parse_args(self):
        super(UaiServiceGetUAISrvAvailableResourceOp, self)._parse_args()
        # add other params in subclasses#

    def cmd_run(self, params):
        super(UaiServiceGetUAISrvAvailableResourceOp, self).cmd_run(params)
        getEnvOp = GetUAISrvAvailableResource(public_key=self.public_key,
                                      private_key=self.private_key,
                                      project_id=self.project_id,
                                      region=self.region,
                                      zone=self.zone)
        succ, rsp = getEnvOp.call_api()
        return succ, rsp
