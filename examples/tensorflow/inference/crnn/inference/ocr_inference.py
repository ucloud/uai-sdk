from local_utils import data_utils,log_utils
from crnn_model import crnn_model
from global_configuration import config
from PIL import Image
import os.path as ops
import cv2
import numpy as np
import tensorflow as tf

from uai.arch.tf_model import TFAiUcloudModel


class ocrModel(TFAiUcloudModel):
	def __init__(self, conf):
		super(ocrModel, self).__init__(conf)
	def load_model(self):
		sess = tf.Session()
		
		x = tf.placeholder(dtype=tf.float32, shape=[1, 32, 100, 3], name='input')
		#define model
		net = crnn_model.ShadowNet(phase='Test', hidden_nums=256, layers_nums=2, seq_length=25, num_classes=37)
		with tf.variable_scope('shadow'):
			net_out = net.build_shadownet(inputdata=x)
		decodes, _ = tf.nn.ctc_beam_search_decoder(inputs=net_out, sequence_length=25*np.ones(1), merge_repeated=False)
		
		sess_config = tf.ConfigProto()
		sess_config.gpu_options.per_process_gpu_memory_fraction = config.cfg.TRAIN.GPU_MEMORY_FRACTION
		sess_config.gpu_options.allow_growth = config.cfg.TRAIN.TF_ALLOW_GROWTH
		sess = tf.Session(config=sess_config)
		
		saver = tf.train.Saver()
		params_file = tf.train.latest_checkpoint(self.model_dir)
		saver.restore(sess=sess, save_path=params_file)

		self.output['sess'] = sess
		self.output['x'] = x
		self.output['y_'] = decodes
		
	def execute(self, data, batch_size):
		sess = self.output['sess']
		x = self.output['x']
		y_ = self.output['y_']
		decoder = data_utils.TextFeatureIO()
		ret = []
		for i in range(batch_size):
			image = np.array(Image.open(data[i]))
			image = cv2.resize(image, (100, 32))
			image = np.expand_dims(image, axis=0).astype(np.float32)
			preds = sess.run(y_, feed_dict={x: image})
			preds = decoder.writer.sparse_tensor_to_str(preds[0])[0]+'\n'
			ret.append(preds)
		return ret
		