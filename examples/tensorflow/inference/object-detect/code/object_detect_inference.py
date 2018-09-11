from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from PIL import Image
import numpy as np
import tensorflow as tf

from uai.arch.tf_model import TFAiUcloudModel
import os
import sys
import tensorflow as tf
from collections import defaultdict
from io import StringIO
import ops as utils_ops
import label_map_util

class ObjectDetectModel(TFAiUcloudModel):
	"""
	Object detect model
	"""

	def __init__(self, conf):
		super(ObjectDetectModel, self).__init__(conf)

	def load_model(self):
                # change params here
                NUM_CLASSES = 37

		sess = tf.Session()
		
		with sess.as_default():
			# Load the model
			od_graph_def = tf.GraphDef()
			with tf.gfile.GFile(os.path.join(self.model_dir, "frozen_inference_graph.pb"), 'rb') as fid:
				serialized_graph = fid.read()
				od_graph_def.ParseFromString(serialized_graph)
				tf.import_graph_def(od_graph_def, name='')

                        # Get handles to input and output tensors
			ops = tf.get_default_graph().get_operations()

                self._sess = sess
                
		all_tensor_names = {output.name for op in ops for output in op.outputs}

		tensor_dict = {}
		for key in ['num_detections', 'detection_boxes', 'detection_scores','detection_classes']:
			tensor_name = key + ':0'
			if tensor_name in all_tensor_names:
				tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(tensor_name)
			
		self._tsdict = tensor_dict

		# now we have a dictionary named category_index, with key as the index and the value the pet cato. name
		label_map = label_map_util.load_labelmap(os.path.join(self.model_dir, "label_map.pbtxt"))
		categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
		self._ct_index = label_map_util.create_category_index(categories)

	def load_image_into_numpy_array(self, image):
		(im_width, im_height) = image.size
		return np.array(image.getdata()).reshape(
					(im_height, im_width, 3)).astype(np.uint8)


	def execute(self, data, batch_size):

		# change params here
		THRESHOLD = 0.5
				
		res = []
		for i in range(batch_size):
			
			image = Image.open(data[i])
			# the array based representation of the image will be used later in order to prepare the
			# result image with boxes and labels on it.
			image_np = self.load_image_into_numpy_array(image)
			# Expand dimensions since the model expects images to have shape: [1, None, None, 3]
			image_np_expanded = np.expand_dims(image_np, axis=0)
			
			sess = self._sess
			image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

			# Run inference
			output_dict = sess.run(self._tsdict, feed_dict={image_tensor: image_np_expanded})
			
			# all outputs are float32 numpy arrays, so convert types as appropriate
			output_dict['num_detections'] = int(output_dict['num_detections'][0])
			output_dict['detection_classes'] = output_dict['detection_classes'][0].astype(np.uint8)
			output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
			output_dict['detection_scores'] = output_dict['detection_scores'][0]

			obj_in_image = []
			for j in range(output_dict['num_detections']):	
				if (output_dict['detection_scores'][j] > THRESHOLD):
					# look up in the dictionary for the indices given in this picture
					res_list = output_dict['detection_boxes'][j].tolist()
					res_list.append(self._ct_index[output_dict['detection_classes'][j]]["name"])
					obj_in_image.append(res_list)
			res.append(obj_in_image)
			
		return res
	
	

		
