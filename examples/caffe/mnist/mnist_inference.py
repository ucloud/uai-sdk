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

import caffe
from uai.arch.caffe_model import CaffeAiUcloudModel

class MnistModel(CaffeAiUcloudModel):
    """ Mnist example model
    """
    def __init__(self, conf):
        super(MnistModel, self).__init__(conf)

    def load_model(self):
        self.model = caffe.Net(self.model_arch_file, self.model_weight_file, caffe.TEST)

    def execute(self, data, batch_size):
        ret = []
        for i in range(batch_size):
            transformer = caffe.io.Transformer({'data': self.model.blobs['data'].data.shape})
            transformer.set_transpose('data', (2, 0, 1))
            transformer.set_raw_scale('data', 255)
            im = caffe.io.load_image(data[i], color=False)
            self.model.blobs['data'].data[...] = transformer.preprocess('data', im)
            self.model.forward()
            prob = self.model.blobs['prob'].data[0].flatten()
            ret_val = str(prob.argsort()[-1]) + '\n'
            ret.append(ret_val)
        return ret
