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

import numpy as np
from PIL import Image
from keras.models import load_model
from keras.models import model_from_json
from uai.arch.keras_model import KerasAiUcloudModel

class MnistModel(KerasAiUcloudModel):
    """ Mnist example model
    """
    def __init__(self, conf):
        super(MnistModel, self).__init__(conf)

    def load_model(self):
        model_json_file = open(self.model_arch_file, 'r')
        model_json = model_json_file.read()
        model_json_file.close()
        model_json = model_from_json(model_json)
        model_json.load_weights(self.model_weight_file)
        self.model = model_json

    def execute(self, data, batch_size):
        ims = []
        for i in range(batch_size):
            im = Image.open(data[i]).resize((28, 28))
            im = np.array(im) / 255.0
            ims.append(im)
        ims = np.array(ims)
        ims = ims.reshape(-1, 784)
        predict_values = self.model.predict(ims)

        ret = []
        for val in predict_values:
            ret_val = str(np.argmax(val).item()) + '\n'
            ret.append(ret_val)
        return ret

