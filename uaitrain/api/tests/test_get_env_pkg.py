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
import unittest

import uaitrain.api.get_env_pkg as pkg_op
import uaitrain.api.base_op as base_op

class TestGetUAITrainEnvPkgAPIOp(unittest.TestCase):
    """docstring for Test"""
    def test_init(self):
        pub_key = 'pub_key'
        priv_key = 'priv_key'
        
        pkg_type = 'pkg_type'
        op = pkg_op.GetUAITrainEnvPkgAPIOp(pub_key, priv_key, pkg_type)
        self.assertEqual(op.cmd_params[base_op.PARAM_ACTION], pkg_op.GET_UAI_TRAIN_ENV_PKG_ACTION)
        self.assertEqual(op.cmd_params[pkg_op.PARAM_PKG_TYPE], pkg_type)

    def test_call_api(self):
        pub_key = 'pub_key'
        priv_key = 'priv_key'
        
        pkg_type = 'pkg_type'

        op = pkg_op.GetUAITrainEnvPkgAPIOp(pub_key, priv_key, "")
        with self.assertRaises(RuntimeError):
            op.call_api()

        """ Test pub_key and priv_key not exist
        """
        op = pkg_op.GetUAITrainEnvPkgAPIOp(pub_key, priv_key, pkg_type)
        succ, result = op.call_api()
        self.assertFalse(succ)

if __name__ == '__main__':
    unittest.main()
        