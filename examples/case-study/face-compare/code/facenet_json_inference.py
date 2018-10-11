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
from scipy import misc
import StringIO
import tensorflow as tf
import numpy as np
import sys
import os
import copy
import argparse
import facenet
import json
import align.detect_face

from uai.arch.tf_model import TFAiUcloudModel
from uai.contrib.image import img_utils

class FaceCompareJsonModel(TFAiUcloudModel):
  """ FaceCompareJsonModel example model
  """

  def __init__(self, conf):
    super(FaceCompareJsonModel, self).__init__(conf)

  def load_model(self):
    sess = tf.Session()

    with sess.as_default():
      # Load the model
      facenet.load_model(self.model_dir)

    # Get input and output tensors
    images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
    embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
    phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")

    self._images_placeholder=images_placeholder
    self._embeddings=embeddings
    self._phase_train_placeholder=phase_train_placeholder
    self._sess = sess

  def preprocess(self, data):
    _, img_list = img_utils.decode_json_to_images(data)
    
    images = []
    for img in img_list:
      img = misc.fromimage(img)
      img = misc.imresize(img, (160, 160), interp='bilinear')
      prewhitened = facenet.prewhiten(img)
      images.append(prewhitened)

    return images

  def compare(self, data):
    images = self.preprocess(data)
    images_placeholder = self._images_placeholder
    phase_train_placeholder = self._phase_train_placeholder
    sess = self._sess
    embeddings = self._embeddings

    feed_dict = {images_placeholder: images, phase_train_placeholder:False }
    emb = sess.run(embeddings, feed_dict=feed_dict)

    if len(images) < 2:
      return -1

    dist = np.sqrt(np.sum(np.square(np.subtract(emb[0,:], emb[1,:]))))
    print('  %1.4f  ' % dist, end='')

    return dist

  def execute(self, data, batch_size):
    results = []
    for i in range(batch_size):
      ret = self.compare(data[i].body)
      if ret == -1:
        results.append(str(-1))
      else:
        results.append(ret.astype('S10'))

    return results

class FaceDetectionJsonModel(TFAiUcloudModel):
  """ FaceCompareModel example model
  """
  def __init__(self, conf):
    super(FaceDetectionJsonModel, self).__init__(conf)

  def load_model(self):
    sess = tf.Session()

    with sess.as_default():
      # Load the model
      pnet, rnet, onet = align.detect_face.create_mtcnn(sess, None)

      self._pent = pnet
      self._rnet = rnet
      self._onet = onet

  def execute(self, data, batch_size):
    minsize = 20 # minimum size of face
    threshold = [ 0.6, 0.7, 0.7 ]  # three steps's threshold
    factor = 0.709 # scale factor

    pnet = self._pent
    rnet = self._rnet
    onet = self._onet

    ret = []
    for i in range(batch_size):
      _, imgs = img_utils.decode_json_to_images(data[i].body)
      img = imgs[0]
      img = misc.fromimage(img)

      boundingboxes, _ = align.detect_face.detect_face(img, minsize, pnet, rnet, onet, threshold, factor)
      boundingboxes = boundingboxes.tolist()
      ret_val = json.dumps({"bounds": boundingboxes})
      ret.append(ret_val)

    return ret
