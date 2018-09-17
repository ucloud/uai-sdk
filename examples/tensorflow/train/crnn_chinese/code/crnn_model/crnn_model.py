#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-9-21 下午6:39
# @Author  : Luo Yao
# @Site    : http://github.com/TJCVRS
# @File    : crnn_model.py
# @IDE: PyCharm Community Edition
"""
Implement the crnn model mentioned in
"An End-to-End Trainable Neural Network for Image-based Sequence
Recognition and Its Application to Scene Text Recognition" paper
"""
import tensorflow as tf
import tensorflow.contrib.slim as slim
from tensorflow.contrib import rnn

from crnn_model import cnn_basenet
from global_configuration import config

CFG = config.cfg


class ShadowNet(cnn_basenet.CNNBaseModel):
    """
        Implement the crnn model for sequence recognition
    """

    def __init__(self, phase, hidden_nums, layers_nums,
                 seq_length, num_classes, rnn_cell_type='lstm'):
        """
        Set the lstm hidden unit numbers, the sequence length and the class numbers

        :param phase:
        :param hidden_nums:
        :param layers_nums:
        :param seq_length:
        :param num_classes:
        :param rnn_cell_type:

        :raise ValueError: if rnn_cell_type not in ['lstm', 'gru']

        """
        super(ShadowNet, self).__init__()
        self._phase = phase
        self._hidden_nums = hidden_nums
        self._layers_nums = layers_nums
        self._seq_length = seq_length
        self._num_classes = num_classes
        self._rnn_cell_type = rnn_cell_type.lower()
        self._train_phase = tf.constant('train', dtype=tf.string)
        self._test_phase = tf.constant('test', dtype=tf.string)
        self._is_training = tf.equal(self._train_phase, phase)
        if self._rnn_cell_type not in ['lstm', 'gru']:
            raise ValueError('rnn_cell_type should be in [\'lstm\', \'gru\']')
        return

    @property
    def phase(self):
        """

        :return:
        """
        return self._phase

    @phase.setter
    def phase(self, value):
        """

        :param value:
        :return: class phase flag
        :raise: ValueError if the lower form of phase flag not in ['train', 'test']
        """
        if not isinstance(value, str):
            raise TypeError('value should be a str \'Test\' or \'Train\'')
        if value.lower() not in ['test', 'train']:
            raise ValueError('value should be a str \'Test\' or \'Train\'')
        self._phase = value.lower()
        return

    def _conv_stage(self, inputdata, out_dims, name=None):
        """
        Traditional conv stage in VGG format
        :param inputdata: The input tensor [NHWC] format
        :param out_dims: Output channel dims
        :return: a NHWC tensor
        """
        conv = self.conv2d(inputdata=inputdata, out_channel=out_dims,
                           kernel_size=3, stride=1, use_bias=False,
                           name=name)
        relu = self.relu(inputdata=conv)
        max_pool = self.maxpooling(inputdata=relu, kernel_size=2, stride=2)
        return max_pool

    def _feature_sequence_extraction(self, inputdata):
        """
        Implement the 2.1 Part Feature Sequence Extraction
        :param inputdata: eg. batch*32*100*3 NHWC format
        :return: a NHWC tensor
        """
        tensor_dict = dict()

        conv1 = self._conv_stage(inputdata=inputdata, out_dims=64, name='conv1')  # batch*16*50*64
        tensor_dict['conv1'] = conv1

        conv2 = self._conv_stage(inputdata=conv1, out_dims=128, name='conv2')  # batch*8*25*128
        tensor_dict['conv2'] = conv2

        conv3 = self.conv2d(inputdata=conv2, out_channel=256,
                            kernel_size=3, stride=1, use_bias=False,
                            name='conv3')  # batch*8*25*256
        relu3 = self.relu(conv3)  # batch*8*25*256
        tensor_dict['conv3'] = conv3
        tensor_dict['relu3'] = relu3

        conv4 = self.conv2d(inputdata=relu3, out_channel=256,
                            kernel_size=3, stride=1, use_bias=False,
                            name='conv4')  # batch*8*25*256
        relu4 = self.relu(conv4)  # batch*8*25*256
        max_pool4 = self.maxpooling(inputdata=relu4, kernel_size=[2, 1], stride=[2, 1],
                                    padding='VALID')  # batch*4*25*256
        tensor_dict['conv4'] = conv4
        tensor_dict['relu4'] = relu4
        tensor_dict['max_pool4'] = max_pool4

        conv5 = self.conv2d(inputdata=max_pool4, out_channel=512,
                            kernel_size=3, stride=1, use_bias=False,
                            name='conv5')  # batch*4*25*512
        conv5_bn5 = self.layerbn(inputdata=conv5, is_training=self._is_training, name='bn5')
        relu5 = self.relu(conv5_bn5)  # batch*4*25*512
        tensor_dict['conv5'] = conv5
        tensor_dict['relu5'] = relu5
        tensor_dict['bn5'] = conv5_bn5

        conv6 = self.conv2d(inputdata=relu5, out_channel=512,
                            kernel_size=3, stride=1, use_bias=False,
                            name='conv6')  # batch*4*25*512
        conv6_bn6 = self.layerbn(inputdata=conv6, is_training=self._is_training, name='bn6')
        relu6 = self.relu(conv6_bn6)  # batch*4*25*512
        max_pool6 = self.maxpooling(inputdata=relu6,
                                    kernel_size=[2, 1], stride=[2, 1])  # batch*2*25*512
        tensor_dict['conv6'] = conv6
        tensor_dict['relu6'] = relu6
        tensor_dict['bn6'] = conv6_bn6
        tensor_dict['max_pool6'] = max_pool6

        conv7 = self.conv2d(inputdata=max_pool6, out_channel=512,
                            kernel_size=2, stride=[2, 1], use_bias=False,
                            name='conv7')  # batch*1*25*512
        relu7 = self.relu(conv7)  # batch*1*25*512
        tensor_dict['conv7'] = conv7
        tensor_dict['relu7'] = relu7
        return relu7, tensor_dict

    def _map_to_sequence(self, inputdata):
        """
        Implement the map to sequence part of the network mainly used to convert the
        cnn feature map to sequence used in later stacked lstm layers
        :param inputdata: NHWC tensor
        :return: a NHWC tensor
        """
        shape = inputdata.get_shape().as_list()
        assert shape[1] == 1  # H of the feature map must equal to 1
        return self.squeeze(inputdata=inputdata, axis=1)

    def _sequence_label(self, inputdata):
        """
        Implement the sequence label part of the network
        :param inputdata:
        :return:
        """
        if self._rnn_cell_type == 'lstm':
            with tf.variable_scope('LSTMLayers'):
                # construct stack lstm rcnn layer
                # forward lstm cell
                fw_cell_list = [rnn.BasicLSTMCell(nh, forget_bias=1.0) for nh in
                                [self._hidden_nums, self._hidden_nums]]
                # Backward direction cells
                bw_cell_list = [rnn.BasicLSTMCell(nh, forget_bias=1.0) for nh in
                                [self._hidden_nums, self._hidden_nums]]

                stack_lstm_layer, _, _ = rnn.stack_bidirectional_dynamic_rnn(
                    fw_cell_list, bw_cell_list, inputdata, parallel_iterations=128, dtype=tf.float32)

                def f1():
                    """

                    :return:
                    """
                    return self.dropout(inputdata=stack_lstm_layer, keep_prob=0.5)

                def f2():
                    """

                    :return:
                    """
                    return stack_lstm_layer

                stack_lstm_layer = tf.cond(self._is_training, f1, f2)

                # [batch, width, 2*n_hidden]
                [batch_s, _, hidden_nums] = inputdata.get_shape().as_list()
                batch_s = tf.shape(inputdata)[0]

                # [batch x width, 2*n_hidden]
                rnn_reshaped = tf.reshape(stack_lstm_layer, [-1, hidden_nums])

                var_w = tf.Variable(tf.truncated_normal([hidden_nums, self._num_classes],
                                                        stddev=0.1), name="w")

                # Doing the affine projection
                # logits = tf.matmul(rnn_reshaped, var_w)
                logits = slim.fully_connected(inputs=rnn_reshaped, num_outputs=self._num_classes,
                                              activation_fn=None)

                logits = tf.reshape(logits, [batch_s, -1, self._num_classes])

                # raw_pred = tf.argmax(tf.nn.softmax(logits),
                #                      axis=2, name='raw_prediction')

                # Swap batch and batch axis
                rnn_out = tf.transpose(logits, (1, 0, 2),
                                       name='transpose_time_major')  # [width, batch, n_classes]
        else:
            with tf.variable_scope('GRULayers'):
                # construct stack fru rcnn layer
                # forward gru cell
                fw_cell_list = [rnn.GRUCell(nh) for nh in
                                [self._hidden_nums, self._hidden_nums]]
                # Backward direction cells
                bw_cell_list = [rnn.GRUCell(nh) for nh in
                                [self._hidden_nums, self._hidden_nums]]

                stack_gru_layer, _, _ = rnn.stack_bidirectional_dynamic_rnn(
                    fw_cell_list, bw_cell_list, inputdata, dtype=tf.float32)

                def f3():
                    """

                    :return:
                    """
                    return self.dropout(inputdata=stack_gru_layer, keep_prob=0.5)

                def f4():
                    """

                    :return:
                    """
                    return stack_gru_layer

                stack_gru_layer = tf.cond(self._is_training, f3, f4)

                # [batch, width, 2*n_hidden]
                [batch_s, _, hidden_nums] = inputdata.get_shape().as_list()

                # [batch x width, 2*n_hidden]
                rnn_reshaped = tf.reshape(stack_gru_layer, [-1, hidden_nums])

                var_w = tf.Variable(tf.truncated_normal([hidden_nums, self._num_classes],
                                                        stddev=0.1),
                                    name="w")

                # Doing the affine projection
                # logits = tf.matmul(rnn_reshaped, var_w)
                logits = slim.fully_connected(inputs=rnn_reshaped, num_outputs=self._num_classes,
                                              activation_fn=None)

                logits = tf.reshape(logits, [batch_s, -1, self._num_classes])

                # raw_pred = tf.argmax(tf.nn.softmax(logits),
                #                      axis=2, name='raw_prediction')

                # Swap batch and batch axis
                rnn_out = tf.transpose(logits, (1, 0, 2),
                                       name='transpose_time_major')  # [width, batch, n_classes]

        return rnn_out

    def build_shadownet(self, inputdata):
        """
        Build the whole crnn model
        :param inputdata:
        :return: The predicted sequence tensor
        """
        with tf.variable_scope('cnn_subnetwork'):
            # first apply the cnn feature extraction stage
            cnn_out, tensor_dict = self._feature_sequence_extraction(inputdata=inputdata)

            # second apply the map to sequence stage
            sequence = self._map_to_sequence(inputdata=cnn_out)

            # third apply the sequence label stage
            net_out = self._sequence_label(inputdata=sequence)

        return net_out, tensor_dict

    def build_shadownet_cnn_subnet(self, inputdata):
        """
        Build the cnn feature extraction part of the crnn model used for classification
        :param inputdata:
        :return:
        """
        # first apply the cnn feture extraction stage
        with tf.variable_scope('cnn_subnetwork'):
            cnn_out = self._feature_sequence_extraction(inputdata=inputdata)

            fc1 = self.fullyconnect(inputdata=cnn_out, out_dim=4096, use_bias=False, name='fc1')

            relu1 = self.relu(inputdata=fc1, name='relu1')

            fc2 = self.fullyconnect(inputdata=relu1, out_dim=CFG.TRAIN.CLASSES_NUMS,
                                    use_bias=False, name='fc2')

        return fc2
