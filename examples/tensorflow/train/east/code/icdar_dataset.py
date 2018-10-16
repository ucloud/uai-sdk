import os

import tensorflow as tf
import numpy as np
import tarfile
import icdar

tf.app.flags.DEFINE_string('tarfile', 
                            'data.tar.gz',
                            'tarfile to uncompress')
tf.app.flags.DEFINE_string('tarpath', '', 'tarfile inner path')

FLAGS = tf.app.flags.FLAGS

TMP_OUTPUT_DIR = "/tmp/"
initialized = False

def prepare_data_once(data_dir):
    def prepare_data():
        # untar data to tmp                                                                                                                                    
        src_tar = os.path.join(data_dir, FLAGS.tarfile)                                                                                                        
        sub_path = FLAGS.tarpath                                                                                                                               
        output_path = TMP_OUTPUT_DIR                                                                                                                           
        print(src_tar)                                                                                                                                         
                
        global initialized                                                                                                                                               
        if initialized is False:                                                                                                                          
            initialized = True
            with tarfile.open(src_tar, "r:gz") as tar:
                tar.extractall(output_path)
            tar.close()
            print('finish untar')

        data_path = os.path.join(TMP_OUTPUT_DIR, sub_path)
        return data_path

    return prepare_data

class EastDataSet(object):                                                                                                                                     
    def __init__(self, data_dir, batch_size, subset='train', use_distortion=True):
        prepare_action = prepare_data_once(data_dir)
        data_path = prepare_action()

        FLAGS.training_data_path = data_path
        generator = icdar.get_batch(num_workers=FLAGS.num_readers,
                                    input_size=FLAGS.input_size,
                                    batch_size=batch_size)

        self.generator = generator
        self.subset = subset

    def gen(self):
        while True:
            data = next(self.generator)
            input_images = np.asarray(data[0])
            input_score_maps = np.asarray(data[2])
            input_geo_maps = np.asarray(data[3])
            input_training_masks = np.asarray(data[4])
            yield input_images, input_score_maps, input_geo_maps, input_training_masks

    def make_batch(self, batch_size):
        dataset = tf.data.Dataset.from_generator(
            self.gen, (tf.float32, tf.float32, tf.float32, tf.float32),
            (tf.TensorShape([batch_size, 512, 512, 3]),
            tf.TensorShape([batch_size, 128, 128, 1]),
            tf.TensorShape([batch_size, 128, 128, 5]),
            tf.TensorShape([batch_size, 128, 128, 1])))

        iterator = dataset.make_one_shot_iterator()

        image_batch, score_map_batch, geo_map_batch, training_mask_batch = iterator.get_next()

        return image_batch, score_map_batch, geo_map_batch, training_mask_batch
