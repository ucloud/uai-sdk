from __future__ import print_function

import argparse
import functools
import itertools
import os
import os.path as ops
import sys
import time

import numpy as np
import tensorflow as tf
import pprint

import six
from six.moves import xrange  # pylint: disable=redefined-builtin

import cv2
import lanms
import model
from icdar import restore_rectangle
from uaitrain.arch.tensorflow import uflag

from tensorflow.core.framework import node_def_pb2
from tensorflow.python.framework import device as pydev
from tensorflow.python.training import device_setter

from typing import List 
from PIL import Image
import cv2

class RestoreParametersAverageValues(tf.train.SessionRunHook):
   """
   Replace parameters with their moving averages.
   This operation should be executed only once, and before any inference.
   """
   def __init__(self, params):
       """
       :param ema:         tf.train.ExponentialMovingAverage
       """
       super(RestoreParametersAverageValues, self).__init__()
       self._params = params
       self._restore_ops = None

   def begin(self):
       """ Create restoring operations before the graph been finalized. """
       east_variables = tf.moving_average_variables()
       self._restore_ops = [tf.assign(x, self._east.average(x)) for x in east_variables]

   def after_create_session(self, session, coord):
       """ Restore the parameters right after the session been created. """
       session.run(self._restore_ops)

def _tower_fn(images):
    with tf.variable_scope(tf.get_variable_scope()):
        f_score, f_geometry = model.model(images, is_training=False)
    return f_score, f_geometry

def get_mode_fn():
    def _mode_fn(features, labels, mode):
        with tf.name_scope('tower_0') as name_scope:
            f_score, f_geometry = _tower_fn(features['feature'])

        variable_averages = tf.train.ExponentialMovingAverage(0.997)
        params = tf.trainable_variables()
        params_averages_op = variable_averages.apply(params)

        predictions = {
            'f_score': f_score,
            'f_geometry': f_geometry,
        }

        export_outputs = {
            'prediction': tf.estimator.export.PredictOutput(predictions)
        }

        return tf.estimator.EstimatorSpec(
            mode=mode,
            predictions=predictions,
            prediction_hooks=[RestoreParametersAverageValues(variable_averages)],
            export_outputs=export_outputs)
    return _mode_fn

def resize_image(im, max_side_len=2400):                                                                                                   
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

def detect(score_map, geo_map, score_map_thresh=0.8, box_thresh=0.1, nms_thres=0.2):                                                
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

class EastPredictor():
    def __init__(self, model_dir):
        self._model_dir = model_dir
        self.output = {}

    def build_east_model(self):
        sess_config = tf.ConfigProto(
            allow_soft_placement=True,
            gpu_options=tf.GPUOptions(force_gpu_compatible=True))

        run_config = tf.contrib.learn.RunConfig(session_config=sess_config, model_dir=self._model_dir)
        classifier = tf.estimator.Estimator(
            model_fn=get_mode_fn(),
            config=run_config)
        self._classifier = classifier

    def do_serve_predict(self, raw_images):
        images = []
        ratio_hs = []
        ratio_ws = []
        for image in raw_images:
            im = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            im_resized, (ratio_h, ratio_w) = resize_image(im)
            ratio_hs.append(ratio_h)
            ratio_ws.append(ratio_w)
            images.append(im_resized)

        batch_size = len(images)
        sess = self.output['sess']
        input_tensor = self.output['input_tensor']
        output_tensors = self.output['output_tensor']

        f_scores, f_geos = sess.run(output_tensors, feed_dict={input_tensor: images})
        fin_result = []
        for i in range(batch_size):
            score = f_scores[i]
            geometry  = f_geos[i]
            score_map = np.reshape(score, (1, score.shape[0], score.shape[1], score.shape[2]))
            geo_map = np.reshape(geometry, (1, geometry.shape[0], geometry.shape[1], geometry.shape[2]))

            boxes = detect(score_map=score_map, geo_map=geo_map)
            if boxes is not None:
                ratio_h = ratio_hs[i]
                ratio_w = ratio_ws[i]
                boxes = boxes[:, :8].reshape((-1, 4, 2))
                boxes[:, :, 0] /= ratio_w
                boxes[:, :, 1] /= ratio_h

                ret = boxes.tolist()
            else:
                ret = ""
            fin_result.append(ret)

        return fin_result

    def load_serve_model(self):                                                                                                                                
        sess = tf.Session()

        """
        You can use 
            saved_model_cli show --dir /tmp/saved_model_dir
            to inspect the saved model for tag-set and signatures
            refer to https://www.tensorflow.org/guide/saved_model#using_savedmodel_with_estimators for more details
        """
        tag = 'serve'
        meta_graph_def = tf.saved_model.loader.load(sess, [tag], self._model_dir)                                                                              
        signature = meta_graph_def.signature_def                                                                                                               
        
        sig = 'prediction'                                                                                                                                     
        input_key = 'input'                                                                                                                                    
        input_tensor_name = signature[sig].inputs[input_key].name
        input_tensor = sess.graph.get_tensor_by_name(input_tensor_name)

        output_tensors = []
        output_key = 'f_score'
        output_tensor_name = signature[sig].outputs[output_key].name
        output_tensor = sess.graph.get_tensor_by_name(output_tensor_name)
        output_tensors.append(output_tensor)

        output_key = 'f_geometry'
        output_tensor_name = signature[sig].outputs[output_key].name
        output_tensor = sess.graph.get_tensor_by_name(output_tensor_name)
        output_tensors.append(output_tensor)

        self.output['sess'] = sess
        self.output['input_tensor'] = input_tensor
        self.output['output_tensor'] = output_tensors

    def export_model(self):
        def serving_input_reciver_fn():
            """ 
            You should change the shape of this placeholder according to your request
            This shape is compatable with do_serve_predict()
            """
            serialized_tf_example = tf.placeholder(shape=[None, None, None, 3], dtype=tf.float32)
            return tf.estimator.export.ServingInputReceiver(serialized_tf_example, serialized_tf_example)

        self._classifier.export_savedmodel('./checkpoint_dir', serving_input_reciver_fn)

if __name__ == '__main__':
    predictor = east_multi_infer.EastPredictor('./checkpoint_dir')
    predictor.build_east_model()
    predictor.export_model()
