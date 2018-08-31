#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-9-22 下午7:47
# @Author  : Luo Yao
# @Site    : http://github.com/TJCVRS
# @File    : write_text_tfrecords.py
# @IDE: PyCharm Community Edition
"""
Write text features into tensorflow records
"""
import os
import os.path as ops
import argparse
import math
import sys

import numpy as np
import tqdm
import cv2
try:
    from cv2 import cv2
except ImportError:
    pass


sys.path.append('/data/code')

from data_provider import data_provider
from local_utils import data_utils
from global_configuration import config
CFG = config.cfg

width = CFG.TRAIN.width


def init_args():
    """

    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_dir', type=str,default='/data/data', help='Where you store the dataset')
    parser.add_argument('--save_dir', type=str,default='/data/output', help='Where you store tfrecords')
    parser.add_argument('--batch_size', type=int,default=32, help='The numbers of examples that every single tfrecord holds')

    return parser.parse_args()


def write_features(dataset_dir, save_dir, batch_size):
    """

    :param dataset_dir:
    :param save_dir:
    :param batch_size:
    :return:
    """
    if not ops.exists(save_dir):
        os.makedirs(save_dir)

    print('Initialize the dataset provider ......')
    provider = data_provider.TextDataProvider(dataset_dir=dataset_dir, annotation_name='sample.txt',
                                              validation_set=True, validation_split=0.05, shuffle='every_epoch',
                                              normalization=None)
    print('Dataset provider intialize complete')

    feature_io = data_utils.TextFeatureIO()

    # write train tfrecords
    print('Start writing training tf records')

    train_images_nums = provider.train.num_examples
    epoch_nums = int(math.ceil(train_images_nums / batch_size))
    for loop in tqdm.tqdm(range(epoch_nums)):
        train_images, train_labels, train_imagenames = provider.train.next_batch(batch_size=batch_size)
        train_images = [cv2.resize(tmp, (width,32)) for tmp in train_images]
        train_images = [bytes(list(np.reshape(tmp, [width * 32*3]))) for tmp in train_images]

        if loop*batch_size+batch_size > train_images_nums:
            train_tfrecord_path = ops.join(save_dir, 'train_feature_{:d}_{:d}.tfrecords'.format(
                loop * batch_size, train_images_nums))
        else:
            train_tfrecord_path = ops.join(save_dir, 'train_feature_{:d}_{:d}.tfrecords'.format(
                loop*batch_size, loop*batch_size+batch_size))
        feature_io.writer.write_features(tfrecords_path=train_tfrecord_path, labels=train_labels, images=train_images,
                                         imagenames=train_imagenames)

    # write test tfrecords
    print('Start writing testing tf records')

    test_images_nums = provider.test.num_examples
    epoch_nums = int(math.ceil(test_images_nums / batch_size))
    for loop in tqdm.tqdm(range(epoch_nums)):
        test_images, test_labels, test_imagenames = provider.test.next_batch(batch_size=batch_size)
        test_images = [cv2.resize(tmp, (32, width)) for tmp in test_images]
        test_images = [bytes(list(np.reshape(tmp, [32 * width * 3]))) for tmp in test_images]

        if loop * batch_size + batch_size > test_images_nums:
            test_tfrecord_path = ops.join(save_dir, 'test_feature_{:d}_{:d}.tfrecords'.format(
                loop*batch_size, test_images_nums))
        else:
            test_tfrecord_path = ops.join(save_dir, 'test_feature_{:d}_{:d}.tfrecords'.format(
                loop * batch_size, loop * batch_size + batch_size))
        feature_io.writer.write_features(tfrecords_path=test_tfrecord_path, labels=test_labels, images=test_images,
                                         imagenames=test_imagenames)

    # write val tfrecords
    print('Start writing validation tf records')

    val_image_nums = provider.validation.num_examples
    epoch_nums = int(math.ceil(val_image_nums / batch_size))
    for loop in tqdm.tqdm(range(epoch_nums)):
        val_images, val_labels, val_imagenames = provider.validation.next_batch(batch_size=batch_size)
        val_images = [cv2.resize(tmp, (32, width)) for tmp in val_images]
        val_images = [bytes(list(np.reshape(tmp, [32 * width * 3]))) for tmp in val_images]

        if loop*batch_size+batch_size > val_image_nums:
            val_tfrecord_path = ops.join(save_dir, 'validation_feature_{:d}_{:d}.tfrecords'.format(
                loop*batch_size, val_image_nums))
        else:
            val_tfrecord_path = ops.join(save_dir, 'validation_feature_{:d}_{:d}.tfrecords'.format(
                loop * batch_size, loop*batch_size+batch_size))
        feature_io.writer.write_features(tfrecords_path=val_tfrecord_path, labels=val_labels, images=val_images,
                                         imagenames=val_imagenames)

    return


if __name__ == '__main__':
    # init args
    args = init_args()
    if not ops.exists(args.dataset_dir):
        raise ValueError('Dataset {:s} doesn\'t exist'.format(args.dataset_dir))

    # write tf records
    write_features(dataset_dir=args.dataset_dir, save_dir=args.save_dir, batch_size=args.batch_size)
