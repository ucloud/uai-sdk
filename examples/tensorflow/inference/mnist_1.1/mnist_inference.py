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

"""A very simple MNIST inferencer.

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


from PIL import Image
import numpy as np
import tensorflow as tf

from uai.arch.tf_model import TFAiUcloudModel

class MnistModel(TFAiUcloudModel):
  """Mnist example_tf model
  """

  def __init__(self, conf):
    super(MnistModel, self).__init__(conf)

  def load_model(self):
    sess = tf.Session()

    """Define MNIST net
       y = x * W + b
       y_ = softmax(y)
    """
    x = tf.placeholder(tf.float32, [None, 784])
    W = tf.Variable(tf.zeros([784, 10]))
    b = tf.Variable(tf.zeros([10]))
    y = tf.matmul(x, W) + b
    y_ = tf.nn.softmax(y)

    """
       Load model from self.model_dir
       The default DIR name is checkpoint_dir/, it should include following files:
         checkpoint: tf checkpoint config file
         model.mod: model file
         model.mod.meta: model meta data file
    """
    saver = tf.train.Saver()
    params_file = tf.train.latest_checkpoint(self.model_dir)
    saver.restore(sess, params_file)

    """
       Register ops into self.output dict.
       So func execute() can get these ops
    """
    self.output['sess'] = sess
    self.output['x'] = x
    self.output['y_'] = y_

  def execute(self, data, batch_size):
    sess = self.output['sess']
    x = self.output['x']
    y_ = self.output['y_']

    imgs = []
    for i in range(batch_size):
      im = Image.open(data[i]).resize((28, 28)).convert('L')
      im = np.array(im)
      im = im.reshape(784)
      im = im.astype(np.float32)
      im = np.multiply(im, 1.0 / 255.0)
      imgs.append(im)

    imgs = np.array(imgs)
    predict_values = sess.run(y_, feed_dict={x: imgs})
    print(predict_values)

    ret = []
    for val in predict_values:
      ret_val = np.array_str(np.argmax(val)) + '\n'
      ret.append(ret_val)
    return ret
