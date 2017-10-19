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

import uaitrain.api.base_op as base_op

class TestBaseUAITrainAPIOp(unittest.TestCase):
    """docstring for Test"""
    def test_init(self):
        action = 'none'
        pub_key = 'pub_key'
        priv_key = 'priv_key'
        project_id = 'project_id'
        region = 'region'
        zone = 'zone'

        op = base_op.BaseUAITrainAPIOp(action, pub_key, priv_key, project_id, region, zone)
        self.assertEqual(op.priv_key, priv_key)
        self.assertEqual(op.pub_key, pub_key)
        self.assertEqual(op.cmd_params[base_op.PARAM_ACTION], action)
        self.assertEqual(op.cmd_params[base_op.PARAM_PUBLIC_KEY], pub_key)
        self.assertEqual(op.cmd_params[base_op.PARAM_PROJECT_ID], project_id)
        self.assertEqual(op.cmd_params[base_op.PARAM_REGION], region)
        self.assertEqual(op.cmd_params[base_op.PARAM_ZONE], zone)

        op = base_op.BaseUAITrainAPIOp(action, pub_key, priv_key, "", "", "")
        self.assertEqual(op.priv_key, priv_key)
        self.assertEqual(op.pub_key, pub_key)
        self.assertEqual(op.cmd_params[base_op.PARAM_ACTION], action)
        self.assertEqual(op.cmd_params[base_op.PARAM_PUBLIC_KEY], pub_key)
        self.assertEqual(op.cmd_params[base_op.PARAM_REGION], base_op.DEFAULT_UAI_TRAIN_REGION)
        self.assertEqual(op.cmd_params[base_op.PARAM_ZONE], base_op.DEFAULT_UAI_TRAIN_ZONE)
        self.assertFalse(base_op.PARAM_PROJECT_ID in op.cmd_params)

    def test_call_api(self):
        action = 'none'
        pub_key = 'pub_key'
        priv_key = 'priv_key'
        op = base_op.BaseUAITrainAPIOp("", "", "", "", "", "")

        with self.assertRaises(RuntimeError):
            op.call_api()

        op = base_op.BaseUAITrainAPIOp(action, "", "", "", "", "")
        with self.assertRaises(RuntimeError):
            op.call_api()

        op = base_op.BaseUAITrainAPIOp(action, pub_key, "", "", "", "")
        with self.assertRaises(RuntimeError):
            op.call_api()

        op = base_op.BaseUAITrainAPIOp(action, pub_key, priv_key, "", "", "")
        succ, ret = op.call_api()
        self.assertFalse(succ)

if __name__ == '__main__':
    unittest.main()