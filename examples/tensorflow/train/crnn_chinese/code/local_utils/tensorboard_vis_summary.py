#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 18-2-28 下午4:49
# @Author  : Luo Yao
# @Site    : http://icode.baidu.com/repos/baidu/personal-code/Luoyao
# @File    : tensorboard_vis_summary.py
# @IDE: PyCharm Community Edition
"""
实现一些tensorboard卷积神经网络可视化工具
"""
import tensorflow as tf


class CNNVisualizer(object):
    """

    """
    def __init__(self):
        pass

    @staticmethod
    def merge_weights_hist(weights_tensor_dict, scope=None, is_merge=True):
        """

        :param weights_tensor_dict:
        :param scope:
        :param is_merge:
        :return:
        """
        ret = dict()

        with tf.variable_scope(scope):
            for tensor_name, tensor in weights_tensor_dict.items():
                ret[tensor_name] = tf.summary.histogram(name=tensor_name, values=tensor)

            if is_merge:
                tensor_list = []
                for _, tensor in ret.items():
                    tensor_list.append(tensor)
                return tf.summary.merge(inputs=tensor_list)
            else:
                return ret

    @staticmethod
    def merge_conv_image(feature_map, scope=None, max_batch=3):
        """

        :param feature_map:
        :param scope:
        :param max_batch:
        :return:
        """
        with tf.variable_scope(scope):
            tensor_shape = feature_map.get_shape().as_list()
            chs = tensor_shape[-1]
            range_stop = chs // 3
            size_splits = [3 for _ in range(range_stop)]
            if len(size_splits) * 3 < chs:
                size_splits.append(chs % 3)
            feature_map_split = tf.split(feature_map, num_or_size_splits=size_splits, axis=3)

            feature_map_concats_1 = []
            concat_step = len(feature_map_split) // 2
            for i in range(0, concat_step, 2):
                concat = tf.concat([feature_map_split[i], feature_map_split[i + 1]], axis=1)
                feature_map_concats_1.append(concat)

            feature_map_concats_2 = []
            concat_step = len(feature_map_concats_1) // 2
            for i in range(0, concat_step, 2):
                concat = tf.concat([feature_map_concats_1[i], feature_map_concats_1[i + 1]], axis=2)
                feature_map_concats_2.append(concat)

            feature_map_concats = tf.concat(feature_map_concats_2, axis=0)

            return tf.summary.image("image", feature_map_concats, max_batch)
