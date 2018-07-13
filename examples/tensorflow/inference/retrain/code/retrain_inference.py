from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import sys
import time

import tensorflow as tf
import os
from PIL import Image

from uai.arch.tf_model import TFAiUcloudModel
from retrain_conf import RetrainJsonConfLoader

class RetrainedClassificationModel(TFAiUcloudModel):

    def __init__(self, conf):
        super(RetrainedClassificationModel, self).__init__(conf)

    def _parse_conf(self, conf):
        retrain_json_conf_loader = RetrainJsonConfLoader(conf)
        self.model_dir = retrain_json_conf_loader.get_model_dir()
        self.input_width = retrain_json_conf_loader.get_input_width()
        self.input_height = retrain_json_conf_loader.get_input_height()

    def read_tensor_from_data(self, data):
        sess = self._sess_pre
        result = sess.run(self._normalized_op, {self._input_data: data})

        return result


    def load_model(self):
        print("Loading model with an input size of: [" + str(self.input_width) + "," + str(self.input_height) + "]")
        graph = tf.Graph()
        graph_def = tf.GraphDef()

        with tf.gfile.FastGFile(os.path.join(self.model_dir, "frozen_inference_graph.pb"), 'rb') as model_f:
            graph_def.ParseFromString(model_f.read())
        with graph.as_default():
            tf.import_graph_def(graph_def, name = '')
                
        input_handler = graph.get_operation_by_name("Placeholder").outputs
        output_handler = graph.get_operation_by_name("final_result").outputs

        sess = tf.Session(graph=graph)

        if (os.path.exists(os.path.join(self.model_dir, "label_map.txt"))):
            with tf.gfile.FastGFile(os.path.join(self.model_dir, "label_map.txt"),"r") as label_map_f:
                label_map = dict()
                for i, cate in enumerate(label_map_f.readlines()):
                    label_map[i] = cate
            self._label_map = label_map

        self._input_handler = input_handler
        self._output_handler = output_handler
        self._sess = sess

        input_height=self.input_height
        input_width=self.input_width
        input_mean=0
        input_std=255
        graph_pre = tf.Graph()

        with graph_pre.as_default():
            input_data = tf.placeholder(tf.string)
            image_reader = tf.image.decode_image(input_data, channels=3)
            float_caster = tf.cast(image_reader, tf.float32)
            dims_expander = tf.expand_dims(float_caster, 0)
            resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
            normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])

        sess_pre = tf.Session(graph=graph_pre)
        self._input_data = input_data
        self._normalized_op = normalized
        self._sess_pre =sess_pre

    def execute(self, data, batch_size):
        
        sess = self._sess
        output_h = self._output_handler
        input_h = self._input_handler
        res = []
        image = []
        height = self.input_height
        width = self.input_width

        for i in range(batch_size):
            image = self.read_tensor_from_data(data[i].body)
            predictions, = sess.run(output_h[0], {input_h[0]: image})
            pred_sorted = predictions.argsort()[::-1][:5]
            single_res = []

            # We can get top-5 if possible
            for type_id in pred_sorted:
                try:
                    cate = self._label_map[type_id][:-1] if self._label_map[type_id][-1] == "\n" else self._label_map[type_id]
                except AttributeError:
                    print("No label map found, returning type id...")
                    cate = type_id
                single_res.append([cate, predictions[type_id]])

            res.append(single_res)

        return res

