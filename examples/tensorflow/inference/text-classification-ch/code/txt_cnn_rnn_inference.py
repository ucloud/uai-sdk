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

"""A text classification cnn/rnn inferencer.

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
from PIL import Image
import numpy as np
import tensorflow as tf
import tensorflow.contrib.keras as kr

from cnn_model import TCNNConfig, TextCNN
from rnn_model import TRNNConfig, TextRNN
from cnews_loader import read_vocab, read_category

from uai.arch.tf_model import TFAiUcloudModel

if sys.version_info[0] > 2:
  is_py3 = True
else:
  reload(sys)
  sys.setdefaultencoding("utf-8")
  is_py3 = False

class TxtClassModel(TFAiUcloudModel):
  """ TxtClass example model
  """

  def __init__(self, conf):
    super(TxtClassModel, self).__init__(conf)

  def load_model(self):
    pass

  def preprocess(self, data):
    return data.body

  def execute(self, data, batch_size):
    pass

class TxtClassCNNModel(TxtClassModel):
  """ TxtClass example model
  """

  def __init__(self, conf):
    super(TxtClassCNNModel, self).__init__(conf)

  def load_model(self):
    sess = tf.Session()
    print('Configuring CNN model...')
    config = TCNNConfig()
    cnn_model = TextCNN(config)

    saver = tf.train.Saver()
    params_file = tf.train.latest_checkpoint(self.model_dir)
    saver.restore(sess, params_file)

    categories, cat_to_id = read_category()
    vocab_dir = 'cnews/cnews.vocab.txt'
    words, word_to_id = read_vocab(vocab_dir)

    self.words = words
    self.word_to_id = word_to_id
    self.categories = categories
    self.cat_to_id = cat_to_id

    self.cnn_model = cnn_model
    self.sess = sess
    print(self.cnn_model)
    print(self.sess)

  def native_content(self, content):
    if not is_py3:
      return content.decode('utf-8')
    else:
      return content

  def execute(self, data, batch_size):
    contents, labels = [], []
    ret = [None] * batch_size

    for i in range(batch_size):
      line = self.preprocess(data[i])
      contents.append(list(self.native_content(line)))

    data_id = []
    for i in range(len(contents)):
      data_id.append([self.word_to_id[x] for x in contents[i] if x in self.word_to_id])

    x_pad = kr.preprocessing.sequence.pad_sequences(data_id, 600)

    print(self.cnn_model)
    print(self.sess)
    feed_dict = {
      self.cnn_model.input_x: x_pad,
      self.cnn_model.keep_prob: 1.0
    }

    results = self.sess.run(self.cnn_model.y_pred_cls, feed_dict=feed_dict)

    i = 0
    for res in results:
      if ret[i] != None:
        i=i+1
        continue

      ret[i] = self.categories[res]
      i=i+1

    return ret

class TxtClassRNNModel(TxtClassModel):
  """ TxtClass example model
  """

  def __init__(self, conf):
    super(TxtClassRNNModel, self).__init__(conf)

  def load_model(self):
    sess = tf.Session()
    print('Configuring CNN model...')
    config = TRNNConfig()
    cnn_model = TextRNN(config)

    saver = tf.train.Saver()
    params_file = tf.train.latest_checkpoint(self.model_dir)
    saver.restore(sess, params_file)

    categories, cat_to_id = read_category()
    vocab_dir = 'cnews/cnews.vocab.txt'
    words, word_to_id = read_vocab(vocab_dir)

    self.words = words
    self.word_to_id = word_to_id
    self.categories = categories
    self.cat_to_id = cat_to_id

    self.cnn_model = cnn_model
    self.sess = sess
    print(self.cnn_model)
    print(self.sess)

  def native_content(self, content):
    if not is_py3:
      return content.decode('utf-8')
    else:
      return content

  def execute(self, data, batch_size):
    contents, labels = [], []
    ret = [None] * batch_size

    for i in range(batch_size):
      line = self.preprocess(data[i])
      contents.append(list(self.native_content(line)))

    data_id= []
    for i in range(len(contents)):
      data_id.append([self.word_to_id[x] for x in contents[i] if x in self.word_to_id])

    x_pad = kr.preprocessing.sequence.pad_sequences(data_id, 600)

    print(self.cnn_model)
    print(self.sess)
    feed_dict = {
      self.cnn_model.input_x: x_pad,
      self.cnn_model.keep_prob: 1.0
    }

    results = self.sess.run(self.cnn_model.y_pred_cls, feed_dict=feed_dict)

    i = 0
    for res in results:
      if ret[i] != None:
        i=i+1
        continue

      ret[i] = self.categories[res]
      i=i+1

    return ret
