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

"""A east text detector inferencer.

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
from PIL import Image
import tensorflow as tf
import numpy as np
import sys
import os
import copy
import argparse
import cv2
import lanms
import model
from icdar import restore_rectangle

from uai.arch.tf_model import TFAiUcloudModel

class EASTTextDetectModel(TFAiUcloudModel):
  """ EASTTextDetectModel example model
  """

  def __init__(self, conf):
    super(EASTTextDetectModel, self).__init__(conf)

  def load_model(self):
    sess = tf.Session()

    with tf.get_default_graph().as_default():
      input_images = tf.placeholder(tf.float32, shape=[None, None, None, 3], name='input_images')
      global_step = tf.get_variable('global_step', [], initializer=tf.constant_initializer(0), trainable=False)

      f_score, f_geometry = model.model(input_images, is_training=False)

      variable_averages = tf.train.ExponentialMovingAverage(0.997, global_step)
      saver = tf.train.Saver(variable_averages.variables_to_restore())

      with sess.as_default():
        model_path = tf.train.latest_checkpoint(self.model_dir)
        saver.restore(sess, model_path)

    self._f_score = f_score
    self._f_geometry = f_geometry
    self._sess = sess
    self._input_images = input_images


  def resize_image(self, im, max_side_len=2400):                                                                                                   
    '''
    resize image to a size multiple of 32 which is required by the network                                                                 
    :param im: the resized image
    :param max_side_len: limit of max image size to avoid out of memory in gpu                                                             
    :return: the resized image and the resize ratio                                                                                        
    '''
    h, w, _ = im.shape                                                                                                                     
    
    resize_w = w                                                                                                                           
    resize_h = h                                                                                                                           
    
    # limit the max side
    if max(resize_h, resize_w) > max_side_len: 
        ratio = float(max_side_len) / resize_h if resize_h > resize_w else float(max_side_len) / resize_w                                  
    else:
        ratio = 1.
    resize_h = int(resize_h * ratio)                                                                                                       
    resize_w = int(resize_w * ratio)                                                                                                       
    
    resize_h = resize_h if resize_h % 32 == 0 else (resize_h // 32 - 1) * 32                                                               
    resize_w = resize_w if resize_w % 32 == 0 else (resize_w // 32 - 1) * 32                                                               
    im = cv2.resize(im, (int(resize_w), int(resize_h)))                                                                                    
    
    ratio_h = resize_h / float(h)                                                                                                          
    ratio_w = resize_w / float(w)                                                                                                          
    
    return im, (ratio_h, ratio_w)

  def detect(self, score_map, geo_map, score_map_thresh=0.8, box_thresh=0.1, nms_thres=0.2):                                                
    '''                                                                                                                                    
    restore text boxes from score map and geo map                                                                                          
    :param score_map:                                                                                                                      
    :param geo_map:                                                                                                                    
    :param score_map_thresh: threshhold for score map                                                                                      
    :param box_thresh: threshhold for boxes                                                                                                
    :param nms_thres: threshold for nms                                                                                                    
    :return:                                                                                                                               
    '''
    if len(score_map.shape) == 4:                                                                                                          
      score_map = score_map[0, :, :, 0]                                                                                                  
      geo_map = geo_map[0, :, :, ]                                                                                                       
    # filter the score map                                                                                                                 
    xy_text = np.argwhere(score_map > score_map_thresh)                                                                                    
    # sort the text boxes via the y axis                                                                                                   
    xy_text = xy_text[np.argsort(xy_text[:, 0])]                                                                                           
    # restore                                                                                                                              

    text_box_restored = restore_rectangle(xy_text[:, ::-1]*4, geo_map[xy_text[:, 0], xy_text[:, 1], :]) # N*4*2                            
    print('{} text boxes before nms'.format(text_box_restored.shape[0]))                                                                   
    boxes = np.zeros((text_box_restored.shape[0], 9), dtype=np.float32)                                                                    
    boxes[:, :8] = text_box_restored.reshape((-1, 8))                                                                                      
    boxes[:, 8] = score_map[xy_text[:, 0], xy_text[:, 1]]                                                                                  
    # boxes = nms_locality.nms_locality(boxes.astype(np.float64), nms_thres)                                                               
    boxes = lanms.merge_quadrangle_n9(boxes.astype('float32'), nms_thres)                                                                                                                                                                   
                                                                                                                                           
    if boxes.shape[0] == 0:                                                                                                                
      return None                                                                                                               
                                                                                                                                           
    # here we filter some low score boxes by the average score map, this is different from the orginal paper                               
    for i, box in enumerate(boxes):                                                                                                        
      mask = np.zeros_like(score_map, dtype=np.uint8)                                                                                    
      cv2.fillPoly(mask, box[:8].reshape((-1, 4, 2)).astype(np.int32) // 4, 1)                                                           
      boxes[i, 8] = cv2.mean(score_map, mask)[0]                                                                                         
    boxes = boxes[boxes[:, 8] > box_thresh]                                                                                                
                                                                                                                                           
    return boxes     

  def execute(self, data, batch_size):
    f_score = self._f_score
    f_geometry = self._f_geometry
    sess = self._sess
    input_images = self._input_images

    imgs = []
    ratio_hs = []
    ratio_ws = []
    for i in range(batch_size):
      im = Image.open(data[i])
      im = np.array(im)
      im_resized, (ratio_h, ratio_w) = self.resize_image(im)
      ratio_hs.append(ratio_h)
      ratio_ws.append(ratio_w)
      imgs.append(im_resized)
      
    score, geometry = sess.run([f_score, f_geometry], feed_dict={input_images: imgs})
    results = []
    for i in range(batch_size):
      score_map = np.reshape(score[i], (1, score[i].shape[0], score[i].shape[1], score[i].shape[2]))
      geo_map = np.reshape(geometry[i], (1, geometry[i].shape[0], geometry[i].shape[1], geometry[i].shape[2]))

      boxes = self.detect(score_map=score_map, geo_map=geo_map)
      if boxes is not None:
        ratio_h = ratio_hs[i]
        ratio_w = ratio_ws[i]
        boxes = boxes[:, :8].reshape((-1, 4, 2))
        boxes[:, :, 0] /= ratio_w
        boxes[:, :, 1] /= ratio_h

        ret = boxes.tolist()
      else:
        ret = ""
      results.append(ret)

    return results

