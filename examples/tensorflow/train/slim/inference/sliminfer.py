# Copyright 2016 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Generic evaluation script that evaluates a model using a given dataset."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import cv2
import os
import tensorflow as tf
import numpy as np

from PIL import Image
from datasets import dataset_factory
from datasets import dataset_utils
from nets import nets_factory
from preprocessing import preprocessing_factory
from uai.arch.tf_model import TFAiUcloudModel
slim = tf.contrib.slim


class slimModel(TFAiUcloudModel):

  def __init__(self,conf):
      super(slimModel,self).__init__(conf)

  def load_model(self):
    sess = tf.Session()
    x = tf.placeholder(tf.float32,shape=[None,None,3])
    
    # read dataset info #
    if dataset_utils.has_labels(self.model_dir):
       labels_to_names = dataset_utils.read_label_file(self.model_dir)
    with open(os.path.join(self.model_dir,'info.json')) as f:
         info_dict = json.load(f)
         _num_classes = info_dict['num_class']+1

 
    # Select the model #
    network_fn = nets_factory.get_network_fn(
        self.conf['infor']['model_name'],
        num_classes=_num_classes,
        is_training=False)
    
    # Select the preprocessing function #
    preprocessing_name = self.conf['infor']['model_name'] if self.conf['infor']['preprocessing_name']=='None' else self.conf['infor']['preprocessing_name']
    image_preprocessing_fn = preprocessing_factory.get_preprocessing(
        preprocessing_name,
        is_training=False)
    eval_image_size = self.conf['infor']['eval_image_size'] if self.conf['infor']['eval_image_size']!='None' else  network_fn.default_image_size
    image = image_preprocessing_fn(x, eval_image_size, eval_image_size)
   
    # inference map 
    imgs = tf.placeholder(tf.float32,shape=[None,None,None,3])
    logits, _ = network_fn(imgs)
    predictions = tf.argmax(logits, 1)
 
    # load model #
    saver = tf.train.Saver()
    params_file = tf.train.latest_checkpoint(self.model_dir)
    saver.restore(sess, params_file)
    
    self.output['x']=x
    self.output['imgs']=imgs
    self.output['predictions']=predictions
    self.output['labels_to_names']=labels_to_names
    self.output['sess'] = sess
    self.output['image'] = image
	
  def execute(self, data, batch_size): 
    sess = self.output['sess']
    x = self.output['x']
    predictions = self.output['predictions']
    labels_to_names = self.output['labels_to_names']
    image = self.output['image']
    imgs = self.output['imgs']

    ret = []
    imgs_value = []
    # preprocessing
    for i in range(batch_size):
      img = Image.open(data[i])
      #because shape of fer image is (48,48) ,we need to expand_dims 
      img = np.expand_dims(np.asarray(img), axis=2)
      img = np.concatenate((img, img, img), axis=-1)
      img = sess.run(image,feed_dict={x: img})
      imgs_value.append(img)
    imgs_value = np.array(imgs_value)
    # inference
    predictions = sess.run(predictions,feed_dict={imgs: imgs_value})
    for i in range(batch_size):
      pre = labels_to_names[predictions[i]]+'\n'
      ret.append(pre)
    return ret
