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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import StringIO

from PIL import Image
import numpy as np
import tensorflow as tf

from uai.arch.tf_model import TFAiUcloudModel

class MnistModel(TFAiUcloudModel):
  def __init__(self, conf):
    super(MnistModel, self).__init__(conf)

  def load_model(self):
    sess = tf.Session()
    x = tf.placeholder(tf.float32, [None, 784])
    W = tf.Variable(tf.zeros([784, 10]))
    b = tf.Variable(tf.zeros([10]))
    y = tf.matmul(x, W) + b
    y_ = tf.nn.softmax(y)

    saver = tf.train.Saver()
    params_file = tf.train.latest_checkpoint("./checkpoint_dir")
    saver.restore(sess, params_file)
    self.output['sess'] = sess
    self.output['x'] = x
    self.output['y_'] = y_

  def execute(self, data, batch_size):
    sess = self.output['sess']
    x = self.output['x']
    y_ = self.output['y_']

    ids = []
    imgs = []
    for i in range(batch_size):
      json_input = json.load(data[i])
      data_id = json_input['appid']
      img_data = json_input['img'].decode('base64')

      im = Image.open(StringIO.StringIO(img_data)).resize((28, 28)).convert('L')
      im = np.array(im)
      im = im.reshape(784)
      im = im.astype(np.float32)
      im = np.multiply(im, 1.0 / 255.0)
      imgs.append(im)
      ids.append(data_id)

    imgs = np.array(imgs)
    print(imgs.shape)
    predict = sess.run(y_, feed_dict={x: imgs})
    ret = []
    for i in range(batch_size):
      ret_val = np.array_str(np.argmax(predict[i]))
      ret_item = json.dumps({ids[i]: ret_val})
      ret.append(ret_item)
    return ret
