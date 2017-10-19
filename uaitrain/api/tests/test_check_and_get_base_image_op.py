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

import uaitrain.api.check_and_get_base_image_op as image_op
import uaitrain.api.base_op as base_op

class TestCheckAndGetUAITrainBasesImageAPIOp(unittest.TestCase):
    """docstring for Test"""
    def test_init(self):
        pub_key = 'pub_key'
        priv_key = 'priv_key'
        
        os_v = 1
        py_v = 1
        ai_frame_v = 1
        acc_id = 1
        op = image_op.CheckAndGetUAITrainBasesImageAPIOp(pub_key, priv_key, os_v, py_v, ai_frame_v, acc_id)
        self.assertEqual(op.cmd_params[base_op.PARAM_ACTION], image_op.CHECK_AND_GET_UAI_TRAIN_BASE_IMAGE_ACTION)
        self.assertEqual(op.cmd_params[image_op.PARAM_OS_VERSION], os_v)
        self.assertEqual(op.cmd_params[image_op.PARAM_PYTHON_VERSION], py_v)
        self.assertEqual(op.cmd_params[image_op.PARAM_AI_FRAME_VERSION], ai_frame_v)
        self.assertEqual(op.cmd_params[image_op.PARAM_ACC_ID], acc_id)

    def test_call_api(self):
        pub_key = 'pub_key'
        priv_key = 'priv_key'
        
        os_v = 2
        py_v = 3
        ai_frame_v = 4
        acc_id = 1

        op = image_op.CheckAndGetUAITrainBasesImageAPIOp(pub_key, priv_key, "", "", "", "")
        with self.assertRaises(RuntimeError):
            op.call_api()

        op = image_op.CheckAndGetUAITrainBasesImageAPIOp(pub_key, priv_key, os_v, "", "", "")
        with self.assertRaises(RuntimeError):
            op.call_api()

        op = image_op.CheckAndGetUAITrainBasesImageAPIOp(pub_key, priv_key, os_v, py_v, "", "")
        with self.assertRaises(RuntimeError):
            op.call_api()

        op = image_op.CheckAndGetUAITrainBasesImageAPIOp(pub_key, priv_key, os_v, py_v, ai_frame_v, "")
        with self.assertRaises(RuntimeError):
            op.call_api()

        """ Test pub_key and priv_key not exist
        """
        op = image_op.CheckAndGetUAITrainBasesImageAPIOp(pub_key, priv_key, os_v, py_v, ai_frame_v, acc_id)
        succ, result = op.call_api()
        self.assertFalse(succ)

if __name__ == '__main__':
    unittest.main()
        