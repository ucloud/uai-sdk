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
import os
from PIL import Image
from scipy import misc
import StringIO
import cv2
import json
import numpy as np
import caffe
from mtcnn import detect_face

from uai.arch.caffe_model import CaffeAiUcloudModel

class MTCNNCpuModel(CaffeAiUcloudModel):
  """ MTCNNModel example model
  """

  def __init__(self, conf):
    json.encoder.FLOAT_REPR = lambda o: format(o, '.8f')
    super(MTCNNCpuModel, self).__init__(conf)

  def load_model(self):
    caffe_model_path = "./model"
    caffe.set_mode_cpu()
    PNet = caffe.Net(caffe_model_path+"/det1.prototxt", caffe_model_path+"/det1.caffemodel", caffe.TEST)
    RNet = caffe.Net(caffe_model_path+"/det2.prototxt", caffe_model_path+"/det2.caffemodel", caffe.TEST)
    ONet = caffe.Net(caffe_model_path+"/det3.prototxt", caffe_model_path+"/det3.caffemodel", caffe.TEST)

    self._PNet = PNet
    self._RNet = RNet
    self._ONet = ONet

  def execute(self, data, batch_size):
    minsize = 20
    threshold = [0.6, 0.7, 0.7]
    factor = 0.709

    PNet = self._PNet
    RNet = self._RNet
    ONet = self._ONet

    ret = []
    for i in range(batch_size):
      img = Image.open(data[i])
      img_array = misc.fromimage(img)

      boundingboxes, points = detect_face(img_array, minsize, PNet, RNet, ONet, threshold, False, factor)
      boundingboxes = boundingboxes.tolist()
      ret_val = json.dumps(boundingboxes)
      ret.append(ret_val)

    return ret
