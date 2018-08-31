#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-9-22 下午6:46
# @Author  : Luo Yao
# @Site    : http://github.com/TJCVRS
# @File    : data_utils.py
# @IDE: PyCharm Community Edition
"""
Implement some utils used to convert image and it's corresponding label into tfrecords
"""
import numpy as np
import tensorflow as tf
import os
import os.path as ops
import re

from local_utils import establish_char_dict
from global_configuration import config

CFG = config.cfg


class FeatureIO(object):
    """
        Implement the base writer class
    """
    def __init__(self, char_dict_path='/data/data/char_dict/char_dict.json',
                 ord_2_index_map_dict_path='/data/data/char_dict/ord_2_index_map.json',
                 index_2_ord_map_dict_path='/data/data/char_dict/index_2_ord_map.json'):
        self.__char_list = establish_char_dict.CharDictBuilder.read_char_dict(char_dict_path)
        self.__ord_2_index_map = establish_char_dict.CharDictBuilder.read_ord_2_index_map_dict(ord_2_index_map_dict_path)
        self.__index_2_ord_map = establish_char_dict.CharDictBuilder.read_index_2_ord_map_dict(index_2_ord_map_dict_path)
        return

    @property
    def char_list(self):
        """

        :return:
        """
        return self.__char_list

    @staticmethod
    def int64_feature(value):
        """
            Wrapper for inserting int64 features into Example proto.
        """
        if not isinstance(value, list):
            value = [value]
        value_tmp = []
        is_int = True
        for val in value:
            if not isinstance(val, int):
                is_int = False
                value_tmp.append(int(float(val)))
        if is_int is False:
            value = value_tmp
        return tf.train.Feature(int64_list=tf.train.Int64List(value=value))

    @staticmethod
    def float_feature(value):
        """
            Wrapper for inserting float features into Example proto.
        """
        if not isinstance(value, list):
            value = [value]
        value_tmp = []
        is_float = True
        for val in value:
            if not isinstance(val, int):
                is_float = False
                value_tmp.append(float(val))
        if is_float is False:
            value = value_tmp
        return tf.train.Feature(float_list=tf.train.FloatList(value=value))

    @staticmethod
    def bytes_feature(value):
        """
            Wrapper for inserting bytes features into Example proto.
        """
        if not isinstance(value, bytes):
            if not isinstance(value, list):
                value = value.encode('utf-8')
            else:
                value = [val.encode('utf-8') for val in value]
        if not isinstance(value, list):
            value = [value]
        return tf.train.Feature(bytes_list=tf.train.BytesList(value=value))

    def char_to_int(self, char):
        """

        :param char:
        :return:
        """
        temp = ord(char)

        return self.__ord_2_index_map[str(temp)]

    def int_to_char(self, number):
        """

        :param number:
        :return:
        """
        if number == '84':
            return '*'
        if number == 84:
            return '*'
        else:
            ord_tmp = self.__index_2_ord_map[str(number)]
            return self.__char_list[ord_tmp]

    def encode_labels(self, labels):
        """
            encode the labels for ctc loss
        :param labels:
        :return:
        """
        encoded_labeles = []
        lengths = []
        for label in labels:
            encode_label = [self.char_to_int(char) for char in label]
            encoded_labeles.append(encode_label)
            lengths.append(len(label))
        return encoded_labeles, lengths

    def sparse_tensor_to_str(self, spares_tensor: tf.SparseTensor):
        """
        :param spares_tensor:
        :return: a str
        """
        indices = spares_tensor.indices
        values = spares_tensor.values
        # values = np.array([self.__ord_2_index_map[str(tmp)] for tmp in values])
        dense_shape = spares_tensor.dense_shape

        number_lists = np.ones(dense_shape, dtype=values.dtype)
        str_lists = []
        res = []
        for i, index in enumerate(indices):
            number_lists[index[0], index[1]] = values[i]
        for number_list in number_lists:
            str_lists.append([self.int_to_char(val) for val in number_list])
        for str_list in str_lists:
            res.append(''.join(c for c in str_list if c != '*'))
        return res


class TextFeatureWriter(FeatureIO):
    """
        Implement the crnn feature writer
    """
    def __init__(self):
        super(TextFeatureWriter, self).__init__()
        return

    def write_features(self, tfrecords_path, labels, images, imagenames):
        """

        :param tfrecords_path:
        :param labels:
        :param images:
        :param imagenames:
        :return:
        """
        assert len(labels) == len(images) == len(imagenames)

        labels, length = self.encode_labels(labels)

        if not ops.exists(ops.split(tfrecords_path)[0]):
            os.makedirs(ops.split(tfrecords_path)[0])

        with tf.python_io.TFRecordWriter(tfrecords_path) as writer:
            for index, image in enumerate(images):
                features = tf.train.Features(feature={
                    'labels': self.int64_feature(labels[index]),
                    'images': self.bytes_feature(image),
                    'imagenames': self.bytes_feature(imagenames[index])
                })
                example = tf.train.Example(features=features)
                writer.write(example.SerializeToString())
                # sys.stdout.write('\r>>Writing {:d}/{:d} {:s} tfrecords'.format(index+1, len(images), imagenames[index]))
                # sys.stdout.flush()
            # sys.stdout.write('\n')
            # sys.stdout.flush()
        return


class TextFeatureReader(FeatureIO):
    """
        Implement the crnn feature reader
    """
    def __init__(self):
        super(TextFeatureReader, self).__init__()
        return

    @staticmethod
    def read_features(tfrecords_dir, num_epochs, flag):
        """

        :param tfrecords_dir:
        :param num_epochs:
        :param flag: 'Train', 'Test', 'Validation'
        :return:
        """
        assert ops.exists(tfrecords_dir)

        if not isinstance(flag, str):
            raise ValueError('flag should be a str in [\'Train\', \'Test\', \'Validation\']')
        if flag.lower() not in ['train', 'test', 'validation']:
            raise ValueError('flag should be a str in [\'Train\', \'Test\', \'Validation\']')

        if flag.lower() == 'train':
            re_patten = r'^train_feature_\d{0,15}_\d{0,15}\.tfrecords\Z'
        elif flag.lower() == 'test':
            re_patten = r'^test_feature_\d{0,15}_\d{0,15}\.tfrecords\Z'
        else:
            re_patten = r'^validation_feature_\d{0,15}_\d{0,15}\.tfrecords\Z'

        tfrecords_list = [ops.join(tfrecords_dir, tmp) for tmp in os.listdir(tfrecords_dir) if re.match(re_patten, tmp)]

        filename_queue = tf.train.string_input_producer(tfrecords_list)
        reader = tf.TFRecordReader()
        _, serialized_example = reader.read(filename_queue)

        features = tf.parse_single_example(serialized_example,
                                           features={
                                               'images': tf.FixedLenFeature((), tf.string),
                                               'imagenames': tf.FixedLenFeature([1], tf.string),
                                               'labels': tf.VarLenFeature(tf.int64),
                                               # 'labels': tf.FixedLenFeature([], tf.int64),
                                           })
        image = tf.decode_raw(features['images'], tf.uint8)
        images = tf.reshape(image, [32,CFG.TRAIN.width, 3])
        labels = features['labels']
        # labels = tf.one_hot(indices=labels, depth=config.cfg.TRAIN.CLASSES_NUMS)
        labels = tf.cast(labels, tf.int32)
        imagenames = features['imagenames']
        return images, labels, imagenames


class TextFeatureIO(object):
    """
        Implement a crnn feture io manager
    """
    def __init__(self):
        """

        """
        self.__writer = TextFeatureWriter()
        self.__reader = TextFeatureReader()
        return

    @property
    def writer(self):
        """

        :return:
        """
        return self.__writer

    @property
    def reader(self):
        """

        :return:
        """
        return self.__reader


if __name__ == '__main__':
    decoder = TextFeatureIO()
    imgs, labels, img_names = decoder.reader.read_features(
        '/home/baidu/DataBase/Sequence_Recognition/Car_Plate/tfrecords',
        num_epochs=None, flag='Test')
    inputdata, input_labels, input_imagenames = tf.train.shuffle_batch(
        tensors=[imgs, labels, img_names], batch_size=128, capacity=1000 + 2 * 128, min_after_dequeue=100,
        num_threads=1)

    sess = tf.Session()

    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(sess=sess, coord=coord)

    with sess.as_default():
        imgs_val, labels_val, img_names_val = sess.run([inputdata, input_labels, input_imagenames])
        print(type(labels_val))
        gt_labels = decoder.reader.sparse_tensor_to_str(labels_val)
        for index, gt_label in enumerate(gt_labels):
            name = img_names_val[index][0].decode('utf-8')
            name = ops.split(name)[1]
            name = name.split('_')[-2]
            print('{:s} --- {:s}'.format(gt_label, name))

        coord.request_stop()
        coord.join(threads=threads)
