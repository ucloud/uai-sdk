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
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import mxnet as mx
from PIL import Image
from collections import namedtuple
from uai.arch.mxnet_model import MXNetAiUcloudModel

class MnistModel(MXNetAiUcloudModel):
    """ Mnist example model
    """
    def __init__(self, conf):
        super(MnistModel, self).__init__(conf)

    def load_model(self):
        sym, self.arg_params, self.aux_params = mx.model.load_checkpoint(self.model_prefix, self.num_epoch)
        self.model = mx.mod.Module(symbol=sym, context=mx.cpu())
   
    def execute(self, data, batch_size):
        BATCH = namedtuple('BATCH', ['data', 'label'])
        self.model.bind(data_shapes=[('data', (batch_size, 1, 28, 28))],
                        label_shapes=[('softmax_label', (batch_size, 10))],
                        for_training=False)
        self.model.set_params(self.arg_params, self.aux_params)

        ret = []
        for i in range(batch_size):
            im = Image.open(data[i]).resize((28, 28))
            im = np.array(im) / 255.0
            im = im.reshape(-1, 1, 28, 28)
            self.model.forward(BATCH([mx.nd.array(im)], None))
            predict_values = self.model.get_outputs()[0].asnumpy()

            val = predict_values[0]
            ret_val = np.array_str(np.argmax(val)) + '\n'
            ret.append(ret_val)
        return ret
