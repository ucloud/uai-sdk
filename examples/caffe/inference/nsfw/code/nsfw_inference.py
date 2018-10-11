from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import os
import sys
import argparse
import glob
import time
from PIL import Image
from StringIO import StringIO
import caffe

from uai.arch.caffe_model import CaffeAiUcloudModel

class NsfwModel(CaffeAiUcloudModel):

	def __init__(self, conf):
		super(NsfwModel, self).__init__(conf)

	
	def load_model(self):
        	self.model = caffe.Net(self.model_arch_file, self.model_weight_file, caffe.TEST)

	def execute(self, data, batch_size):
		ret = []
		for i in range(batch_size):
			"""1
			"""
			# Load transformer
			# Note that the parameters are hard-coded for best results
			caffe_transformer = caffe.io.Transformer({'data': self.model.blobs['data'].data.shape})
			caffe_transformer.set_transpose('data', (2, 0, 1))  # move image channels to outermost
			caffe_transformer.set_mean('data', np.array([104, 117, 123]))  # subtract the dataset-mean value in each channel
			caffe_transformer.set_raw_scale('data', 255)  # rescale from [0, 1] to [0, 255]
			caffe_transformer.set_channel_swap('data', (2, 1, 0))  # swap channels from RGB to BGR

			""" 2
			"""
			pimg = data[i]
			
			""" resize
			"""
			sz = (256, 256)
			im = Image.open(pimg)
			if (im.mode != "RGB"):
				im = im.convert('RGB')
			imr = im.resize(sz, resample=Image.BILINEAR)
			fh_im = StringIO()
			imr.save(fh_im, format='JPEG')
			fh_im.seek(0)
			
			img_data_rs = bytearray(fh_im.read())
			image = caffe.io.load_image(StringIO(img_data_rs))

			H, W, _ = image.shape
			_, _, h, w = self.model.blobs['data'].data.shape
			h_off = int(max((H - h) / 2, 0))
			w_off = int(max((W - w) / 2, 0))
			
			print ("h:" + str(type(h)))
			print ("w:" + str(type(w)))
			print ("h_off:" + str(type(h_off)))
			print ("w_off:" + str(type(w_off)))
			
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
			ret.append(outputs[1])

		return ret


