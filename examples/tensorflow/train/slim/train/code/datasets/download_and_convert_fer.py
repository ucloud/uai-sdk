# Copyright 2016 The TensorFlow Authors. All Rights Reserved.
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
r"""Downloads and converts picture data to TFRecords of TF-Example protos.

This module reads the pictures and creates two TFRecord datasets: one for train
and one for test. Each TFRecord dataset is comprised of a set of TF-Example
protocol buffers, each of which contain a single image and label.

The script should take several minutes to run.

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import random
import tensorflow as tf
import json

from datasets import dataset_utils

# The height and width of each image.
_IMAGE_SIZE_WIDTH = 48
_IMAGE_SIZE_HEIGHT = 48



def _add_to_tfrecord(filename, tfrecord_writer,labels_to_class_names, offset=0):
  """Loads pic data from the filename and writes files to a TFRecord.

  Args:
    filename: The filename of one picture .
    tfrecord_writer: The TFRecord writer to use for writing.
    offset: An offset into the absolute number of images previously written.

  Returns:
    The new offset.
  """
  image = tf.gfile.FastGFile(filename,'r').read()
  label = labels_to_class_names[filename.split('/')[-2]]

  with tf.Graph().as_default():
    with tf.Session('') as sess:
      example = dataset_utils.image_to_tfexample(
            image, b'jpg', _IMAGE_SIZE_HEIGHT, _IMAGE_SIZE_WIDTH, label)
      tfrecord_writer.write(example.SerializeToString())

  return offset + 1


def _get_output_filename(dataset_dir, split_name):
  """Creates the output filename.

  Args:
    dataset_dir: The dataset directory where the dataset is stored.
    split_name: The name of the train/test split.

  Returns:
    An absolute file path.
  """
  return '%s/fer_%s.tfrecord' % (dataset_dir, split_name)





def run(dataset_dir,pic_path):
  """Runs the conversion operation.

  Args:
    dataset_dir: The dataset directory where the dataset is stored.
  """
  if not tf.gfile.Exists(dataset_dir):
    tf.gfile.MakeDirs(dataset_dir)

  training_filename = _get_output_filename(dataset_dir, 'train')
  testing_filename = _get_output_filename(dataset_dir, 'test')

  if tf.gfile.Exists(training_filename) and tf.gfile.Exists(testing_filename):
    print('Dataset files already exist. Exiting without re-creating them.')
    return

  class_names = os.listdir(pic_path)
  labels_to_class_names = dict(zip(class_names,range(len(class_names))))
  
  picnames=[]
  for label in class_names:
      alabel_path=os.path.join(pic_path,label)
      names=os.listdir(alabel_path)
      picnames.extend([os.path.join(alabel_path,name) for name in names])
  random.shuffle(picnames)      
  
  train_picnames = picnames[:int(0.7*len(picnames))]
  test_picnames = picnames[int(0.7*len(picnames)):]
  # First, process the training data:
  with tf.python_io.TFRecordWriter(training_filename) as tfrecord_writer:
    offset = 0
    for name in train_picnames:
        offset = _add_to_tfrecord(name, tfrecord_writer, labels_to_class_names, offset)

  # Next, process the testing data:
  with tf.python_io.TFRecordWriter(testing_filename) as tfrecord_writer:
       offset = 0
       for name in test_picnames:
           offset = _add_to_tfrecord(name, tfrecord_writer, labels_to_class_names, offset)

  # Finally, write the labels file:
  labels_to_class_names = dict(zip(labels_to_class_names.values(),labels_to_class_names.keys())) 
  dataset_utils.write_label_file(labels_to_class_names, dataset_dir)
  with open(os.path.join(dataset_dir,'info.json'),'w') as f:
    info=json.dumps({'num_class':len(class_names),'num_sample_train':len(train_picnames),'num_sample_test':len(test_picnames)})
    f.write(info)

  print('\nFinished converting the dataset in the {}!'.format(pic_path))
  print('\nThe tfrecord files,info.json and labels file is located in the {}'.format(dataset_dir))
