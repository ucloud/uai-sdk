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

import tensorflow as tf
import numpy as np
from uai.arch.tf_model import TFAiUcloudModel
from uai.arch_conf.tf_conf import TFServingJsonConfLoader

class TFServingAiUcloudModel(TFAiUcloudModel):
    """
        Base model class for user defined Tensorflow Model
    """
    def __init__(self, conf=None, model_type='tensorflow'):
        super(TFServingAiUcloudModel, self).__init__(conf, model_type)
        self.output = {}
        self._parse_conf(conf)
        self.model = self.load_model()

    def _parse_conf(self, conf):
        """
            Parse Tensorflow related config
            Args:
                conf: key/val object for AI architecture specific config
        """
        tf_json_conf_loader = TFServingJsonConfLoader(conf)
        self.model_dir = tf_json_conf_loader.get_model_dir()
        self.input_info = tf_json_conf_loader.get_input_set()
        self.output_info = tf_json_conf_loader.get_output_set()
        self.tag = tf_json_conf_loader.get_tag_set()
        self.signature = tf_json_conf_loader.get_signature()

    def load_model(self):
        sess = tf.Session()
        meta_graph_def = tf.saved_model.loader.load(sess, self.tag, self.model_dir)
        signature = meta_graph_def.signature_def

        input_key = self.input_info["name"]
        input_tensor_name = signature[self.signature].inputs[input_key].name
        input_tensor = sess.graph.get_tensor_by_name(input_tensor_name)

        output_key_list = self.output_info["name"]
        output_tensor_list = []
        for output_key in output_key_list:
            output_tensor_name = signature[self.signature].outputs[output_key].name
            output_tensor = sess.graph.get_tensor_by_name(output_tensor_name)
            output_tensor_list.append(output_tensor)

        self.output['sess'] = sess
        self.output['input_tensor'] = input_tensor
        self.output['output_tensor'] = output_tensor_list

    def preprocess(self, data):
        return data.body

    def execute(self, data, batch_size):
        sess = self.output['sess']
        input_tensor = self.output['input_tensor']
        output_tensor = self.output['output_tensor']
        print(output_tensor)

        imgs = []
        '''Provide auto batching method now
           TODO: provide config for auto-batching
        '''
        for i in range(batch_size):
            img_pre = self.preprocess(data[i])
            img = np.array(img_pre)
            imgs.append(img)
        imgs = np.array(imgs)

        output_tensor = sess.run(output_tensor, feed_dict={input_tensor: imgs})
        return output_tensor
