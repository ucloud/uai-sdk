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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import os
import sys
import argparse
import glob
from PIL import Image
from StringIO import StringIO
from uai.contrib.media import opencv_rtsp

import caffe

from uai.arch.caffe_model import CaffeAiUcloudModel

class NsfwStreamModel(CaffeAiUcloudModel):

    def __init__(self, conf):
        super(NsfwStreamModel, self).__init__(conf)

    def nsfw_score(self, image):
        caffe_transformer = self.caffe_transformer

	""" resize
	"""
        fh_im = StringIO() 
        image.save(fh_im, format='png')
        fh_im.seek(0)
        image = caffe.io.load_image(fh_im)

	H, W, _ = image.shape
	_, _, h, w = self.model.blobs['data'].data.shape
	h_off = int(max((H - h) / 2, 0))
        w_off = int(max((W - w) / 2, 0))
            
	crop = image[h_off:h_off + h, w_off:w_off + w, :]
	transformed_image = caffe_transformer.preprocess('data', crop)
	transformed_image.shape = (1,) + transformed_image.shape

	""" 3
	"""
	input_name = self.model.inputs[0]
	all_outputs = self.model.forward_all(blobs=["prob"],
			**{input_name: transformed_image})

	""" 4
	"""
	outputs = all_outputs['prob'][0].astype(float)
        return outputs[1]

    def stream_process(self):
        rtsp_p = opencv_rtsp.UaiOpenCVRtspProcessor('rtsp://localhost:1235/test.sdp', 256, 256)
            
        while(1):                                                                                                                                              
            img = rtsp_p.get_next_n_frame(5)
            if img is None:
                continue
            score = self.nsfw_score(img)
            print(score)

    def load_model(self):
        self.model = caffe.Net(self.model_arch_file, self.model_weight_file, caffe.TEST)

        caffe_transformer = caffe.io.Transformer({'data': self.model.blobs['data'].data.shape})
        caffe_transformer.set_transpose('data', (2, 0, 1))  # move image channels to outermost
        caffe_transformer.set_mean('data', np.array([104, 117, 123]))  # subtract the dataset-mean value in each channel
        caffe_transformer.set_raw_scale('data', 255)  # rescale from [0, 1] to [0, 255]
        caffe_transformer.set_channel_swap('data', (2, 1, 0))  # swap channels from RGB to BGR

        self.caffe_transformer = caffe_transformer

        self.stream_process()

    def execute(self, data, batch_size):
        pass