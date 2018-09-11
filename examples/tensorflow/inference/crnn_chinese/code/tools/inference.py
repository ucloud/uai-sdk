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
sys.path.append('/data/code')
#import matplotlib.pyplot as plt
try:
    from cv2 import cv2
except ImportError:
    pass

from crnn_model import crnn_model
from global_configuration import config
from local_utils import log_utils, data_utils

#logger = log_utils.init_logger()


class ocrModel(TFAiUcloudModel):
      def __init__(self,conf):
          super(ocrModel,self).__init__(conf)
      def load_model(self):
          sess=tf.session()
          x=tf.placeholder(dtype=tf.float32, shape=[1, 32, 100, 3], name='input')
          net=crnn_model.ShadowNet(phase=phase_tensor, hidden_nums=256, layers_nums=2, seq_length=15, num_classes=config.cfg.TRAIN.CLASSES_NUMS, rnn_cell_type='lstm')
          with tf.variable_scope('shadow'):
               net_out, tensor_dict = net.build_shadownet(inputdata=inputdata)
          decodes, _ = tf.nn.ctc_beam_search_decoder(inputs=net_out, sequence_length=20*np.ones(1), merge_repeated=False)
          
          saver = tf.train.Saver()
          params_file = tf.train.latest_checkpoint(self.model_dir)
          saver.restore(sess=sess, save_path=params_file)
          self.output['sess'] = sess
          self.output['x'] = x
          self.output['y'] = decodes
      def execute(self,data,batch_size):
          sess=self.output['sess']
          x=self.output['x']
          y=self.output['y']
          decoder = data_utils.TextFeatureIO()
          ret=[]
          for i in range(batch_size):
              image = Image.open(data[i])
              image = cv2.cvtColor(np.asarray(image),cv2.COLOR_RGB2BGR)
              image = cv2.resize(image, (100, 32))
              image = np.expand_dims(image, axis=0).astype(np.float32)
              preds = sess.run(decodes, feed_dict={x:image})
              preds = decoder.writer.sparse_tensor_to_str(preds[0])[0]+'\n'
              ret.append(preds)
          return ret
