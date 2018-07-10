from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import sys

import tensorflow as tf
import os
from PIL import Image

from uai.arch.tf_model import TFAiUcloudModel
from retrain_conf import RetrainJsonConfLoader

class RetrainDetectModel(TFAiUcloudModel):

    def __init__(self, conf):
        super(RetrainDetectModel, self).__init__(conf)

    def _parse_conf(self, conf):
        retrain_json_conf_loader = RetrainJsonConfLoader(conf)
        self.model_dir = retrain_json_conf_loader.get_model_dir()
        self.model_struct = retrain_json_conf_loader.get_model_struct()
        self.input_width = retrain_json_conf_loader.get_input_width()
        self.input_height = retrain_json_conf_loader.get_input_height()

    def read_tensor_from_image_file(self, file_name,
                                input_height=299,
                                input_width=299,
                                input_mean=0,
                                input_std=255):
      input_name = "file_reader"
      output_name = "normalized"
      file_reader = tf.read_file(file_name, input_name)
      if file_name.endswith(".png"):
        image_reader = tf.image.decode_png(file_reader, channels=3, name="png_reader")
      elif file_name.endswith(".gif"):
        image_reader = tf.squeeze(tf.image.decode_gif(file_reader, name="gif_reader"))
      elif file_name.endswith(".bmp"):
        image_reader = tf.image.decode_bmp(file_reader, name="bmp_reader")
      else:
        image_reader = tf.image.decode_jpeg(file_reader, channels=3, name="jpeg_reader")
      float_caster = tf.cast(image_reader, tf.float32)
      dims_expander = tf.expand_dims(float_caster, 0)
      resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
      normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
      sess = tf.Session()
      result = sess.run(normalized)

      return result

    def load_model(self):
        sess = tf.Session()
        print("Loading model: " + self.model_struct + " with an input size of: [" + str(self.input_width) + "," + str(self.input_height) + "]")
        
        with sess.as_default():
            with tf.gfile.FastGFile(os.path.join(self.model_dir, "frozen_inference_graph.pb"), 'rb') as model_f:
                graph_def = tf.GraphDef()
                graph_def.ParseFromString(model_f.read())
                tf.import_graph_def(graph_def, name = '')
                input_handler = tf.get_default_graph().get_operation_by_name("Placeholder").outputs[0]
                output_handler = tf.get_default_graph().get_operation_by_name("final_result").outputs[0]

        if (os.path.exists(os.path.join(self.model_dir, "label_map.txt"))):
            with tf.gfile.FastGFile(os.path.join(self.model_dir, "label_map.txt"),"r") as label_map_f:
                label_map = dict()
                for i, cate in enumerate(label_map_f.readlines()):
                    label_map[i] = cate
            self._label_map = label_map

        self._input_handler = input_handler
        self._output_handler = output_handler
        self._sess = sess

    def execute(self, data, batch_size):

        THRESHOLD = 0.5
        
        sess = self._sess
        output_h = self._output_handler
        input_h = self._input_handler
        res = []
        image = []
        for i in range(batch_size):
        
            img = Image.open(data[i])
            temp = os.path.join(self.model_dir, "temp" + str(i) + ".jpg")
            img.save(temp)
	    height = self.input_height
	    width = self.input_width
	    image.append(self.read_tensor_from_image_file(temp, input_height=height,input_width=width))
            os.remove(temp)
            
            predictions, = sess.run(output_h, {input_h: image[i]})

            pred_sorted = predictions.argsort()[::-1]
            single_res = []
            for type_id in pred_sorted:
                if (predictions[type_id] > THRESHOLD):
                    try:
                        cate = self._label_map[type_id][:-1] if self._label_map[type_id][-1] == "\n" else self._label_map[type_id]
                    except AttributeError:
                        print("No label map found, returning type id...")
                        cate = type_id
                    single_res.append([cate, predictions[type_id]])
                else:
                    break
            res.append(single_res)

        return res
