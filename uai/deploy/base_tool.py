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
import os
import sys
import json
import time
import requests
from ucloud.ufile import putufile, downloadufile
#from ucloud.logger import logger, set_log_file
from uai.utils.logger import uai_logger
from uai.utils.utils import _verfy_ac, save_json
from uai.utils.retcode_checker import check_retcode
from uai.utils.retcode_checker import NORMAL_CONDITION
from uai.arch_conf.base_conf import DeleteConf

MAX_POLL_STEPS = 200
UFILE_JSON = './ufile.json'
DEPLOY_ID_FILE = './deploy_id.log'

class UaiDeployTool(object):
    def __init__(self, platform, parser):
        self.platform = platform
        self.parser = parser

        self.conf_params = {}
        self.files = []
        self.request_params = {}
        self.check_params = {}

        self._add_args()
        self.id_file = open(DEPLOY_ID_FILE, 'w')

    def _add_args(self):
        """ AI Arch Specific Deploy Tool should implement its own _add_args
        """
        raise UserWarning("UaiDeployTool._add_args Unimplemented")

    def deploy(self):
        """ Deploy the model and code files, request the server
        """
        self._upload_model()
        self._upload_code()
        self._upload_json_file()
        self._request_server()
        self._check_server()

    def _format_check_params(self):
        self.check_params['Action'] = 'Check'
        self.check_params['PublicKey'] = self.request_params['PublicKey']
        self.check_params['Id'] = self.deploy_response['Id']

    def _format_check_url(self):
        self.check_url = 'http://api.ucloud.cn:80'

    def _check_request(self):
        max_poll_steps = MAX_POLL_STEPS
        uai_logger.debug('=' * 10 + 'Start poll the state of deploy' + '=' * 10)
        uai_logger.debug('the url to check the state of deploy: {0}'.format(
            self.check_url))

        self.check_params['Signature'] = _verfy_ac(
            self.request_params['PrivateKey'], self.check_params)
        for step in range(max_poll_steps):
            uai_logger.debug(
                    'the step {0} to poll the state of the deploy'.format(
                    step))
            r = requests.get(self.check_url, params=self.check_params)
            uai_logger.debug('the result of step {0}'.format(step))
            if r.status_code != requests.codes.ok:
                uai_logger.warning('================================')
                uai_logger.warning('Check Error, PLS check your connection')
                break
            json_data = json.loads(r.text)
            r_info = {}
            for k, v in json_data.items():
                if isinstance(k, unicode):
                    k = k.encode('utf-8')
                if isinstance(v, unicode):
                    v = v.encode('utf-8')
                r_info[k] = v
            if check_retcode(r_info) != NORMAL_CONDITION:
                uai_logger.warning('Deploy Error: {0}'.format(r_info['Message']))
                break
            else:
                if r_info['Status'] == 'SUCCESS':
                    uai_logger.info(
                        'Building Success, the domain of your deploy application is {0}'.
                        format(r_info['Domain']))
                    self.id_file.write('URL: {0}\n'.format(r_info['Domain']))
                    break
                elif r_info['Status'] == 'BUILDING':
                    uai_logger.info('Building Image Now')
                    time.sleep(5)
                    continue
                elif r_info['Status'] == 'PUSHIMAGE':
                    uai_logger.info('Pushing Image Now')
                    time.sleep(5)
                    continue
                elif r_info['Status'] == 'PAASDEPLOY':
                    uai_logger.info('Creating App On PAAS Now')
                    time.sleep(5)
                    continue
                elif r_info['Status'] == 'FAILED':
                    uai_logger.error('Error Message: {0} '.format(r_info[
                        'Message']))
                    break

    def _check_server(self):
        self._format_check_params()
        self._format_check_url()
        self._check_request()

    def _format_request_params(self):
        self.request_params['Action'] = 'Deploy'
        self.request_params['BucketName'] = self.conf_params['docker'][
            'ufile']['bucket']
        self.request_params['ConfigName'] = UFILE_JSON
        self.request_params['PrivateKey'] = self.conf_params['docker'][
            'ufile']['private_key']
        self.request_params['PublicKey'] = self.conf_params['docker']['ufile'][
            'public_key']

    def _format_request_url(self):
        self.request_url = 'http://api.ucloud.cn:80'

    def _make_request(self):
        self.request_params['Signature'] = _verfy_ac(
            self.request_params['PrivateKey'], self.request_params)
        uai_logger.info('=====================================')
        uai_logger.info('Send AI Service Deploy Request')
        uai_logger.debug(self.request_url)
        uai_logger.debug(self.request_params)

        r = requests.get(self.request_url,
                         params=self.request_params,
                         timeout=600)
        uai_logger.info('=====================================')
        uai_logger.info('Get API Request Response:')
        uai_logger.info(r.status_code)
        uai_logger.debug('the deploy request url: {0}'.format(r.url))
        uai_logger.debug('the all info {0}'.format(r.text))
        if r.status_code != requests.codes.ok:
            uai_logger.info('Deploy Error! Please Retry')
            sys.exit(0)
        json_data = json.loads(r.text)

        r_info = {}
        for k, v in json_data.items():
            if isinstance(k, unicode):
                k = k.encode('utf-8')
            if isinstance(v, unicode):
                v = v.encode('utf-8')
            r_info[k] = v

        self.deploy_response = r_info
        uai_logger.info('Start Setting Up, Your application ID is {0}'.
                        format(r_info['Id']))
        self.id_file.write('Id: {0}\n'.format(r_info['Id']))

    def _request_server(self):
        self._format_request_params()
        self._format_request_url()
        self._make_request()

    def _get_all_files(self, dir_path):
        """Visit the all file in the dir
        """
        file_list = []
        for root, dirs, files in os.walk(dir_path):
            curr_list = [os.path.join(root, i) for i in files]
            file_list += curr_list
        return file_list

    def _reformat_conf_params(self):
        uai_logger.debug('Reformat the config params')
        self.conf_params['docker']['ufile']['files'] = self.files
        self.conf_params['docker']['ufile'].pop('code_files')
        self.conf_params['docker']['ufile'].pop('model_dir')
        uai_logger.debug('Reformat the config params successful')

    def _upload_file(self, file_path):
        """ Upload the file to the ufile 
        """
        public_key = self.conf_params['docker']['ufile']['public_key']
        private_key = self.conf_params['docker']['ufile']['private_key']
        bucket = self.conf_params['docker']['ufile']['bucket']
        uai_logger.debug('Start upload file to the bucket {0}'.format(
            self.conf_params['docker']['ufile']['bucket']))

        handler = putufile.PutUFile(public_key, private_key)
        local_file = file_path
        key = local_file
        uai_logger.info('Upload >> key: {0}, local file: {1}'.format(key, local_file))

        ret, resp = handler.putfile(bucket, key, local_file)
        assert resp.status_code == 200, 'upload seems something error'
        uai_logger.debug('upload local file :{0} to ufile key= {1} successful'.
                    format(local_file, key))
        self.files.append(key)

    def _upload_model(self):
        """ Upload the all model files in model dir
        """
        model_dir = self.conf_params['docker']['ufile']['model_dir']
        model_files_list = self._get_all_files(model_dir)
        for model_file in model_files_list:
            self._upload_file(model_file)
        uai_logger.info('Upload model {0} successful'.format(model_dir))

    def _upload_code(self):
        """ Upload the all code files
        """
        code_files_list = self.conf_params['docker']['ufile']['code_files']
        for file in code_files_list:
            self._upload_file(file)
        uai_logger.info('Upload code {0} successful'.format(code_files_list))

    def _upload_json_file(self):
        """ Upload the json file
        """
        ufile_json = UFILE_JSON
        # reformat the conf_params
        self._reformat_conf_params()
        save_json(self.conf_params, ufile_json)
        self._upload_file(ufile_json)

class UaiDeleteTool(object):
    def __init__(self, parser):
        self.parser = parser
        self.conf_params = {}
        self.delete_params = {}
        self._add_args()

    def _add_args(self):
        delete_conf = DeleteConf(self.parser)
        self.conf_params = delete_conf.conf_params

    def _format_delete_param(self):
        self.delete_params['Action'] = 'DeleteTask'
        self.delete_params['PrivateKey'] = self.conf_params['private_key']
        self.delete_params['PublicKey'] = self.conf_params['public_key']
        self.delete_params['TaskId'] = self.conf_params['task_id']

    def _format_delete_url(self):
        self.delete_url = 'http://api.ucloud.cn:80'

    def _delete_request(self):
        private_key = self.conf_params['private_key']
        task_id = self.delete_params['TaskId']
        self.delete_params['Signature'] = _verfy_ac(private_key,
                                                     self.delete_params)
        uai_logger.debug('==' * 10)
        uai_logger.info("Start to make delete task {0} request".format(task_id))
        r = requests.get(self.delete_url, params=self.delete_params)
        if r.status_code != requests.codes.ok:
            uai_logger.debug('================================')
            uai_logger.warning('Delete Error, PLS check your connection')
            sys.exit(0)
        json_data = json.loads(r.text)
        r_info = {}
        for k, v in json_data.items():
            if isinstance(k, unicode):
                k = k.encode('utf-8')
            if isinstance(v, unicode):
                v = v.encode('utf-8')
            r_info[k] = v
        if check_retcode(r_info) != NORMAL_CONDITION:
            uai_logger.error('Delete Error: {0}'.format(r_info['Message']))
            sys.exit(0)
        else:
            uai_logger.info('Delete task id {0} successful'.format(task_id))

    def del_task(self):
        """ Delete the task of specified task id
        """
        self._format_delete_param()
        self._format_delete_url()
        self._delete_request()
        pass
