import json
from uai.utils.logger import uai_logger
from uai.operation.base_operation import BaseUaiServiceOp
from uai.api.get_uai_available_env_pkg import GetUAIAvailableEnvPkgOp
from uai.api.check_uai_base_img_exist import CheckUAIBaseImgExistOp

UCLOUD_API_URL = 'http://api.ucloud.cn'

class UaiServiceCheckBaseImgExistOp(BaseUaiServiceOp):

    def __init__(self, parser):
        super(UaiServiceCheckBaseImgExistOp, self).__init__(parser)

    def _add_args(self, parser):
        super(UaiServiceCheckBaseImgExistOp, self)._add_args(parser)
        args_parser = parser.add_argument_group()

        args_parser.add_argument(
            '--os',
            type=str,
            default='ubuntu',
            required=False,
            help='the type of the docker os, default as ubuntu')
        args_parser.add_argument(
            '--python_v',
            type=str,
            default='python',
            required=False,
            help='the python version of the docker, such as python-2.7.6')

        if hasattr(self, 'platform') is True:
            args_parser.add_argument(
                '--ai_arch_v',
                type=str,
                default=self.platform,
                required=False,
                help='AI architecture and specific version')
        else:
            args_parser.add_argument(
                '--ai_arch_v',
                type=str,
                default='tensorflow',
                required=False,
                help='AI architecture and specific version, such as tensorflow-1.1.0')

        #add other params in subclasses#

    def _parse_args(self):
        super(UaiServiceCheckBaseImgExistOp, self)._parse_args()
        self.os_version = self.params['os'] if 'os' in self.params else ''
        self.python_version = self.params['python_v'] if 'python_v' in self.params else ''
        self.ai_frame_version = self.params['ai_arch_v'] if 'ai_arch_v' in self.params else ''
        # add other params in subclasses#

    def _translate_pkg_to_id(self, pkgtype, pkglist):
        resultlist = []
        uai_logger.info("Start translate {0} package to their id, packages: {1}".format(pkgtype, pkglist))
        for avpkg in self.rsp['PkgSet']:
            for pkg in pkglist:
                if pkgtype == 'os' or pkgtype == 'python_v' or pkgtype == 'ai_arch_v':
                    versionsplit = pkg.rfind('-')
                    if versionsplit >= 0:
                        if avpkg["PkgName"] == pkg[:versionsplit] and (
                                avpkg["PkgVersion"] == "" or avpkg["PkgVersion"] == pkg[versionsplit + 1:]):
                            pkglist.remove(pkg)
                            resultlist.append(avpkg["PkgId"])
                    elif versionsplit < 0:
                        if avpkg["PkgName"] == pkg:
                            pkglist.remove(pkg)
                            resultlist.append(avpkg["PkgId"])
                else:
                    if avpkg["PkgName"] == pkg:
                        pkglist.remove(pkg)
                        resultlist.append(avpkg["PkgId"])

        if len(pkglist) != 0:
            uai_logger.error("Some {0} package is not supported: {1}".format(pkgtype, pkglist))
            raise RuntimeError("Some {0} package is not supported: {1}".format(pkgtype, pkglist))

        uai_logger.info("End translate {0} package to their id, result: {1}".format(pkgtype, resultlist))
        return resultlist

    def cmd_run(self, params):
        super(UaiServiceCheckBaseImgExistOp, self).cmd_run(params)
        envOp = GetUAIAvailableEnvPkgOp(public_key=self.public_key,
                                      private_key=self.private_key,
                                      project_id=self.project_id,
                                      region=self.region,
                                      zone=self.zone)
        succ, self.rsp = envOp.call_api()
        if self.rsp["RetCode"] != 0:
            uai_logger.error("Fail: [checkBase][getEnv] {0}".format(self.rsp))
            raise RuntimeError("Fail: [checkBase][getEnv] {0}".format(self.rsp))

        self.os_version = self._translate_pkg_to_id('os', self.params['os'].split(','))[0]
        self.python_version = self._translate_pkg_to_id('python_v', self.params['python_v'].split(','))[0]
        self.ai_frame_version = self._translate_pkg_to_id('ai_arch_v', self.params['ai_arch_v'].split(','))[0]

        checkOp = CheckUAIBaseImgExistOp(public_key=self.public_key,
                                      private_key=self.private_key,
                                      project_id=self.project_id,
                                      region=self.region,
                                      zone=self.zone,
                                      os_version=self.os_version,
                                      python_version=self.python_version,
                                      ai_frame_version=self.ai_frame_version)
        succ, rsp = checkOp.call_api()
        return succ, rsp
        # add other params in subclasses#