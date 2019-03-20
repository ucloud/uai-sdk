# Copyright 2019 The UAI-SDK Authors. All Rights Reserved. 
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
import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import load_model

from uai.arch.tf_model import TFAiUcloudModel

class MnistModel(TFAiUcloudModel):
  """Mnist example_tf model
  """

  def __init__(self, conf):
    super(MnistModel, self).__init__(conf)

  def load_model(self):
    model_path = os.path.join(self.model_dir, 'mnist.h5')
    model = load_model(model_path)
    self._model = model

  def execute(self, data, batch_size):
    imgs = []
    for i in range(batch_size):
      im = Image.open(data[i]).resize((28, 28)).convert('L')
      im = np.array(im)
      #im = im.reshape(784)
      im = im.astype(np.float32)
      im = np.multiply(im, 1.0 / 255.0)
      imgs.append(im)

    imgs = np.array(imgs)
    print(self._model)
    predict_values = self._model.predict(imgs)
    print(predict_values)

    ret = []
    for val in predict_values:
      ret_val = str(np.argmax(val).item()) + '\n'
      ret.append(ret_val)
    return ret