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

import sys
import requests
import json

import uai.test_tool.comparator as comparator
from uai.test_tool.base_tester import BaseTester

class HttpTester(BaseTester):
    def __init__(self, conf_file, port):
        super(HttpTester, self).__init__()
        self.port = port
        self.test_url = 'http://0.0.0.0:' + port + '/service'
        self.conf_file = conf_file

    def load_data(self):
        data_file = open(self.conf_file, 'rb')
        data = json.load(data_file)
        return data

    def do_test(self):
        data = self.load_data()
        type = data['result_type']
        data_list = data['data_list']

        data_comparator = comparator.get_comparator(type)
        if data_comparator == None:
            print("Unknow comparator type:{}".format(type))
            self.test_fail()
            return

        for i in data_list:
            print("Test for {}:{}".format(i, data_list[i]))
            input = open(i, 'rb').read()
            expect_val = data_list[i]
            resp = requests.post(self.test_url, data=input)
            if resp.status_code != requests.codes.ok:
                print("Http error: {}".format(resp.status_code))
                self.test_fail()
                return
            if data_comparator.compare(expect_val, resp) == False:
                print("Inference Check Error")
                self.test_fail()
                return

            self.pass_cnt += 1
            print("Test Pass for {}".format(i))

        self.test_success()
        return
