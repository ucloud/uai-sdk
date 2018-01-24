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

""" A very simple Inception-v3 inferencer.
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

class InceptionModel(TFServingAiUcloudModel):
    """ Inception-v3 example model
    """
    def __init__(self, conf):
        super(InceptionModel, self).__init__(conf)

    def load_model(self):
        super(InceptionModel, self).load_model()

    def execute(self, data, batch_size):
        output_tensor = super(InceptionModel, self).execute(data, batch_size)

        ret = []
        for i in range(batch_size):
            classes_arr = output_tensor[0]
            ret.append(classes_arr[i][0])
        return ret