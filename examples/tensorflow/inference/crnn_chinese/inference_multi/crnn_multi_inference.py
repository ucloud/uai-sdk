#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-9-29 下午3:56
# @Author  : Luo Yao
# @Site    : http://github.com/TJCVRS
# @File    : demo_shadownet.py
# @IDE: PyCharm Community Edition
"""
Use shadow net to recognize the scene text
"""
import tensorflow as tf
import os.path as ops
import numpy as np
import cv2
import argparse
import sys
from PIL import Image
sys.path.append('/data/crnn')
#import matplotlib.pyplot as plt
try:
    from cv2 import cv2
except ImportError:
    pass

from crnn_model import crnn_model
from global_configuration import config
from local_utils import log_utils, data_utils
from uai.arch.tf_model import TFAiUcloudModel
import crnn_multi_infer

#logger = log_utils.init_logger()


class CrnnModel(TFAiUcloudModel):
    def __init__(self,conf):
        super(CrnnModel,self).__init__(conf)

    def load_model(self):
        predictor = crnn_multi_infer.crnnPredictor('./checkpoint_dir')
        predictor.build_crnn_model()
        self._predictor = predictor

    def execute(self,data,batch_size):
        predictor = self._predictor
        ret=[]

        images = []
        for i in range(batch_size):
            image = Image.open(data[i])
            images.append(image)

        word = predictor.do_predict(images)
        return word
