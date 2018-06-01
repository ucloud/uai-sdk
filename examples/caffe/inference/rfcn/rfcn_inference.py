#!/usr/bin/env python

# --------------------------------------------------------
# R-FCN
# Copyright (c) 2016 Yuwen Xiong
# Licensed under The MIT License [see LICENSE for details]
# Written by Yuwen Xiong
# --------------------------------------------------------

"""
Demo script showing detections in sample images.

See README.md for installation instructions before running.
"""

import _init_paths
from fast_rcnn.config import cfg
from fast_rcnn.test import im_detect
from fast_rcnn.nms_wrapper import nms
import numpy as np
import caffe, os, sys, cv2

from uai.arch.caffe_model import CaffeAiUcloudModel

class RFCNModel(CaffeAiUcloudModel):
    """ Mnist example model
    """
    def __init__(self, conf):
        super(RFCNModel, self).__init__(conf)

    def load_model(self):
        caffe.set_mode_gpu()
        prototxt = 'models/test_agnostic.prototxt'
        caffemodel = "models/resnet101_rfcn_final.caffemodel"
        cfg.TEST.HAS_RPN = True
        self.net = caffe.Net(prototxt, caffemodel, caffe.TEST)

    def execute(self, data, batch_size):
        ret = []
        for i in range(batch_size):
            img_array = np.asarray(bytearray(data[i].read()), dtype=np.uint8)
            im = cv2.imdecode(img_array, -1)

            scores, boxes = im_detect(self.net, im) 

            ret_val=str(scores) + '\n' + str(boxes) + "\n"
            ret.append(ret_val)
        return ret
