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
import os
import argparse

from uai.test_tool.http_tester import HttpTester


"""
Note: helper test running tool for local development test
                          also for funcationality varificiation of AI service
                          during AI task deployment/update
Usage: python run_test.py --data_conf=data.json
       data.json in format of
       {
           result_type: ""
           data_list: {
              "file_to_test1": result1,
              "file_to_test2": result2,
              ...
           }
       }
       result_type tells the type of the return value, we currently only support:
         1. uai.test_tool.comparator.TYPE_STR ("str")
         2. uai.test_tool.comparator.TYPE_JSON ("json")

       data_list contains a list of data_file/result pairs, data_file points to the location 
         of the data_file contain the request input, result contains the expected inference 
         result in format of 'result_type'
"""

def run_http_test(data_conf, port):
    tester = HttpTester(data_conf, port)
    tester.do_test()

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='AI Simple Test Arg Parser')
    parser.add_argument("--data_conf", action="store", default="json.conf",
                        dest="data_conf", help="json file holding all data_file/result pairs to test")
    parser.add_argument("--port", action="store", default="8080",
                        dest="port", help="server listen port")
    args = parser.parse_args()

    data_conf = args.data_conf
    port = args.port

    if os.path.isfile(data_conf):
        run_http_test(data_conf, port)
    else:
        print('Test Fail')
        sys.exit(1)

