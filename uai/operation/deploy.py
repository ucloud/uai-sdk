import time
from uai.utils.logger import uai_logger
from uai.operation.base_operation import BaseUaiServiceOp
from uai.operation.checkdeploy import CheckUAIDeployProgressOp
from uai.api.get_uai_available_env_pkg import GetUAIAvailableEnvPkgOp
from uai.api.deploy_uai_service import DeployUAIService


class UaiServiceDeployByUfileOp(BaseUaiServiceOp):
    def __init__(self, parser):
        super(UaiServiceDeployByUfileOp, self).__init__(parser)

    def _add_args(self, parser):
        super(UaiServiceDeployByUfileOp, self)._add_args(parser)
        args_parser = parser.add_argument_group()
        args_parser.add_argument(
            '--service_id',
            type=str,
            required=True,
            help='the uai service id')
        args_parser.add_argument(
            '--deploy_weight',
            type=str,
            required=False,
            default=10,
            help='the version weight of uai service, int between 1 to 100 '
                 '(Optional, default is 10 when not specified)')
        args_parser.add_argument(
            '--ufile_url',
            type=str,
            required=True,
            help='the url path given by ufile')
        args_parser.add_argument(
            '--os',
            type=str,
            default='ubuntu',
            help='the type of the docker os')
        args_parser.add_argument(
            '--language',
            type=str,
            default='python-2.7.6',
            help='the language of the docker')
        args_parser.add_argument(
            '--ai_arch_v',
            type=str,
            required=True,
            help='AI architecture and specific version')
        args_parser.add_argument(
            '--os_deps',
            type=str,
            help='the dependency of the ubuntu apt-get')
        args_parser.add_argument(
            '--pip',
            type=str,
            help='the dependency of the python pip')
        # add other params in subclasses#

    def _parse_args(self):
        super(UaiServiceDeployByUfileOp, self)._parse_args()
        self.service_id = self.params['service_id']
        self.ufile_url = self.params['ufile_url']

        self.os_version = self.params['os'] if 'os' in self.params else ''
        self.python_version = self.params['python_v'] if 'python_v' in self.params else ''
        self.ai_frame_version = self.params['ai_arch_v'] if 'ai_arch_v' in self.params else ''

        self.os_deps = self.params['os_deps'] if 'os_deps' in self.params else ''
        self.pip = self.params['pip'] if 'pip' in self.params else ''

        self.deploy_weight = self.params['deploy_weight'] if 'deploy_weight' in self.params else ''
        self.description = self.params['description'] if 'description' in self.params else ''
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
        super(UaiServiceDeployByUfileOp, self).cmd_run(params)
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
        self.python_v = self._translate_pkg_to_id('python_v', self.params['language'].split(','))[0]
        self.ai_arch_v = self._translate_pkg_to_id('ai_arch_v', self.params['ai_arch_v'].split(','))[0]
        if len(self.os_deps) != 0:
            self.apt_list = self._translate_pkg_to_id('os_deps', self.os_deps.split(','))
        else:
            self.apt_list = []
        if len(self.pip) != 0:
            self.pip_list = self._translate_pkg_to_id('pip', self.pip.split(','))
        else:
            self.pip_list = []

        startOp = DeployUAIService(public_key=self.public_key,
                                   private_key=self.private_key,
                                   project_id=self.project_id,
                                   region=self.region,
                                   zone=self.zone,
                                   service_id=self.service_id,
                                   ufile_url=self.ufile_url,
                                   os_version=self.os_version,
                                   python_v=self.python_v,
                                   ai_frame_v=self.ai_arch_v,
                                   pip_list=self.pip_list,
                                   apt_list=self.apt_list,
                                   deploy_weight=self.deploy_weight)

        succ, rsp = startOp.call_api()
        if succ == False:
            return False, rsp

        for i in range(0, 200):
            deploy_process_succ, deploy_process_rsp = CheckUAIDeployProgressOp(public_key=self.public_key,
                                                                               private_key=self.private_key,
                                                                               project_id=self.project_id,
                                                                               service_id=self.service_id,
                                                                               srv_version=rsp['SrvVersion']).call_api()
            if deploy_process_succ == False \
                    or deploy_process_rsp['Status'] == 'Error' \
                    or deploy_process_rsp['Status'] == 'Started' \
                    or deploy_process_rsp['Status'] == 'ToStart':
                break
            time.sleep(10)
        return succ, rsp