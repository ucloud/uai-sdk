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

""" A very simple MNIST inferencer.
    The model that loaded was saved by SavedModelBuilder.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow as tf
from PIL import Image
import json
from uai.arch.tf_serving import TFServingAiUcloudModel

class MnistModel(TFServingAiUcloudModel):
    """ Mnist example model
    """
    def __init__(self, conf):
        super(MnistModel, self).__init__(conf)

    def load_model(self):
        super(MnistModel, self).load_model()

    def preprocess(self, data):
        im = Image.open(data).resize((28, 28)).convert('L')
        im = np.array(im)
        im = im.reshape(784)
        im = im.astype(np.float32)
        im = np.multiply(im, 1.0 / 255.0)
        return im

    def execute(self, data, batch_size):
        # call TFServingAiUcloudModel.execute to do the inference
        output_tensor = super(MnistModel, self).execute(data, batch_size)

        ret = []
        for i in range(batch_size):
            scores_arr = output_tensor[0]
            ret_val = np.array_str(np.argmax(scores_arr[i])) + '\n'
            ret.append(ret_val)

        return ret
