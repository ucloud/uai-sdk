from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from PIL import Image

from uai.arch.tf_model import TFAiUcloudModel

import numpy as np
import tensorflow as tf
import cifar10
import cv2

label_dict={0:'airplane',1:'automobile',2:'bird',3:'cat',4:'deer',5:'dog',6:'frog',7:'horse',8:'ship',9:'truck'}

class cifarModel(TFAiUcloudModel):
	def __init__(self, conf):
        super(cifarModel, self).__init__(conf)
    def load_model(self):
        sess = tf.Session()
		
        x = tf.placeholder(dtype=tf.float32, shape=[1, 24, 24, 3], name='input')
        #inferece
        pred = tf.argmax(cifar10.inference(x),axis=1)
        #load model
        saver = tf.train.Saver()
        params_file = tf.train.latest_checkpoint(self.model_dir)
        saver.restore(sess=sess, save_path=params_file)

        self.output['sess'] = sess
        self.output['x'] = x
        self.output['y_'] = pred

    def execute(self, data, batch_size):
        sess = self.output['sess']
        x = self.output['x']
        y_ = self.output['y_']
        ret = []
        for i in range(batch_size):
            image = Image.open(data[i])
            image = cv2.cvtColor(np.asarray(image),cv2.COLOR_RGB2BGR)
            image = cv2.resize(image, (24, 24))
            mean=np.mean(image)
            std=np.std(image)
            image=(image-mean)/max(std,1/np.sqrt(image.size))
            image = np.expand_dims(image, axis=0).astype(np.float32)
            preds = sess.run(y_, feed_dict={x: image})
            pred_label=label_dict[preds[0]]
            ret.append(pred_label)
        return ret

