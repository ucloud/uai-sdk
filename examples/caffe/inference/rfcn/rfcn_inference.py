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

CLASSES = ('__background__',
           'aeroplane', 'bicycle', 'bird', 'boat',
           'bottle', 'bus', 'car', 'cat', 'chair',
           'cow', 'diningtable', 'dog', 'horse',
           'motorbike', 'person', 'pottedplant',
           'sheep', 'sofa', 'train', 'tvmonitor')

class RFCNNmsModel(CaffeAiUcloudModel):
    """ Mnist example model
    """
    def __init__(self, conf):
        super(RFCNNmsModel, self).__init__(conf)

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
            CONF_THRESH = 0.8
            NMS_THRESH = 0.3
            cand = []

            for cls_ind, cls in enumerate(CLASSES[1:]):
                cls_ind += 1 # because we skipped background
                cls_boxes = boxes[:, 4:8]
                cls_scores = scores[:, cls_ind]
                dets = np.hstack((cls_boxes,
                                  cls_scores[:, np.newaxis])).astype(np.float32)
                keep = nms(dets, NMS_THRESH)
                dets = dets[keep, :]

                one = [cls, dets, CONF_THRESH]
                cand.append(one)

            rects = []
            cas = []
            for item in cand:
                class_name = item[0]
                dets = item[1]
                thresh = item[2]
                inds = np.where(dets[:, -1] >= thresh)[0]
                if len(inds) == 0:
                    continue
                for j in inds:
                    bbox = dets[j, :4]
                    score = dets[j, -1]
                    rect = [bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]]
                    rects.append(rect)
                    cs = [class_name, score]
                    cas.append(cs)
            ret_val=str(cas) + '\n' + str(rects) + "\n"
            ret.append(ret_val)
        return ret
