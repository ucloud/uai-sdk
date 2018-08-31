#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-9-22 下午1:39
# @Author  : Luo Yao
# @Site    : http://github.com/TJCVRS
# @File    : train_shadownet.py
# @IDE: PyCharm Community Edition
"""
Train shadow net script
"""
import argparse
import os
import os.path as ops
import sys
import time

import numpy as np
import tensorflow as tf
import pprint

sys.path.append('/data/code')

from crnn_model import crnn_model
from local_utils import data_utils, log_utils, tensorboard_vis_summary
from global_configuration import config
from uaitrain.arch.tensorflow import uflag

tf.app.flags.DEFINE_string('dataset_dir','/data/data/tfrecords','data path')
tf.app.flags.DEFINE_string('weights_path',None,'weight path')
FLAGS = tf.app.flags.FLAGS

logger = log_utils.init_logger()

'''def init_args():
    """
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_dir', type=str,default='/data/data/tfrecords' ,help='Where you store the dataset')
    parser.add_argument('--weights_path', type=str,default=None ,help='Where you store the pretrained weights')

    return parser.parse_args()
'''

def train_shadownet():
    """

    :param dataset_dir:
    :param weights_path:
    :return:
    """
    # input_tensor = tf.placeholder(dtype=tf.float32, shape=[config.cfg.TRAIN.BATCH_SIZE, 32, 100, 3],
    #                               name='input_tensor')

    # decode the tf records to get the training data
    decoder = data_utils.TextFeatureIO().reader
    images, labels, imagenames = decoder.read_features(FLAGS.dataset_dir, num_epochs=None,
                                                       flag='Train')
    # images_val, labels_val, imagenames_val = decoder.read_features(dataset_dir, num_epochs=None,
    #                                                                flag='Validation')
    inputdata, input_labels, input_imagenames = tf.train.shuffle_batch(
        tensors=[images, labels, imagenames], batch_size=config.cfg.TRAIN.BATCH_SIZE,
        capacity=1000 + 2 * config.cfg.TRAIN.BATCH_SIZE, min_after_dequeue=100, num_threads=1)

    # inputdata_val, input_labels_val, input_imagenames_val = tf.train.shuffle_batch(
    #     tensors=[images_val, labels_val, imagenames_val], batch_size=config.TRAIN.BATCH_SIZE,
    #     capacity=1000 + 2 * config.TRAIN.BATCH_SIZE,
    #     min_after_dequeue=100, num_threads=1)

    inputdata = tf.cast(x=inputdata, dtype=tf.float32)
    phase_tensor = tf.placeholder(dtype=tf.string, shape=None, name='phase')
    accuracy_tensor = tf.placeholder(dtype=tf.float32, shape=None, name='accuracy_tensor')

    # initialize the net model
    shadownet = crnn_model.ShadowNet(phase=phase_tensor, hidden_nums=256, layers_nums=2, seq_length=15,
                                     num_classes=config.cfg.TRAIN.CLASSES_NUMS, rnn_cell_type='lstm')

    with tf.variable_scope('shadow', reuse=False):
        net_out, tensor_dict = shadownet.build_shadownet(inputdata=inputdata)

    cost = tf.reduce_mean(tf.nn.ctc_loss(labels=input_labels, inputs=net_out,
                                         sequence_length=20*np.ones(config.cfg.TRAIN.BATCH_SIZE)))

    decoded, log_prob = tf.nn.ctc_beam_search_decoder(net_out,
                                                      20*np.ones(config.cfg.TRAIN.BATCH_SIZE),
                                                      merge_repeated=False)

    sequence_dist = tf.reduce_mean(tf.edit_distance(tf.cast(decoded[0], tf.int32), input_labels))

    global_step = tf.Variable(0, name='global_step', trainable=False)

    starter_learning_rate = config.cfg.TRAIN.LEARNING_RATE
    learning_rate = tf.train.exponential_decay(starter_learning_rate, global_step,
                                               config.cfg.TRAIN.LR_DECAY_STEPS, config.cfg.TRAIN.LR_DECAY_RATE,
                                               staircase=True)

    update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
    with tf.control_dependencies(update_ops):
        optimizer = tf.train.AdadeltaOptimizer(learning_rate=learning_rate).minimize(loss=cost, global_step=global_step)
        # optimizer = tf.train.MomentumOptimizer(learning_rate=learning_rate, momentum=0.9).minimize(
        #     loss=cost, global_step=global_step)

    # Set tf summary
    tboard_save_path = '/data/output/'
    if not ops.exists(tboard_save_path):
        os.makedirs(tboard_save_path)

    visualizor = tensorboard_vis_summary.CNNVisualizer()

    # training过程summary
    train_cost_scalar = tf.summary.scalar(name='train_cost', tensor=cost)
    train_accuracy_scalar = tf.summary.scalar(name='train_accuray', tensor=accuracy_tensor)
    train_seq_scalar = tf.summary.scalar(name='train_seq_dist', tensor=sequence_dist)
    train_conv1_image = visualizor.merge_conv_image(feature_map=tensor_dict['conv1'],
                                                    scope='conv1_image')
    train_conv2_image = visualizor.merge_conv_image(feature_map=tensor_dict['conv2'],
                                                    scope='conv2_image')
    train_conv3_image = visualizor.merge_conv_image(feature_map=tensor_dict['conv3'],
                                                    scope='conv3_image')
    train_conv7_image = visualizor.merge_conv_image(feature_map=tensor_dict['conv7'],scope='conv7_image')
    lr_scalar = tf.summary.scalar(name='Learning_Rate', tensor=learning_rate)

    weights_tensor_dict = dict()
    for vv in tf.trainable_variables():
        if 'conv' in vv.name:
            weights_tensor_dict[vv.name[:-2]] = vv
    train_weights_hist_dict = visualizor.merge_weights_hist(
        weights_tensor_dict=weights_tensor_dict, scope='weights_histogram', is_merge=False)

    train_summary_merge_list = [train_cost_scalar, train_accuracy_scalar, train_seq_scalar, lr_scalar,
                                train_conv1_image, train_conv2_image, train_conv3_image]
    for _, weights_hist in train_weights_hist_dict.items():
        train_summary_merge_list.append(weights_hist)
    train_summary_op_merge = tf.summary.merge(inputs=train_summary_merge_list)

    # validation过程summary
    # val_cost_scalar = tf.summary.scalar(name='val_cost', tensor=cost)
    # val_seq_scalar = tf.summary.scalar(name='val_seq_dist', tensor=sequence_dist)
    # val_accuracy_scalar = tf.summary.scalar(name='val_accuracy', tensor=accuracy_tensor)

    # test_summary_op_merge = tf.summary.merge(inputs=[val_cost_scalar, val_accuracy_scalar,
    #                                                  val_seq_scalar])

    # Set saver configuration
    restore_variable_list = [tmp.name for tmp in tf.trainable_variables()]
    saver = tf.train.Saver()
    model_save_dir = '/data/output'
    if not ops.exists(model_save_dir):
        os.makedirs(model_save_dir)
    train_start_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    model_name = 'shadownet_{:s}.ckpt'.format(str(train_start_time))
    model_save_path = ops.join(model_save_dir, model_name)

    # Set sess configuration
    sess_config = tf.ConfigProto()
    sess_config.gpu_options.per_process_gpu_memory_fraction = config.cfg.TRAIN.GPU_MEMORY_FRACTION
    sess_config.gpu_options.allow_growth = config.cfg.TRAIN.TF_ALLOW_GROWTH
    sess_config.gpu_options.allocator_type = 'BFC'

    sess = tf.Session(config=sess_config)

    summary_writer = tf.summary.FileWriter(tboard_save_path)
    summary_writer.add_graph(sess.graph)

    # Set the training parameters
    train_epochs = config.cfg.TRAIN.EPOCHS

    print('Global configuration is as follows:')
    pprint.pprint(config.cfg)

    with sess.as_default():

        if FLAGS.weights_path is None:
            logger.info('Training from scratch')
            init = tf.global_variables_initializer()
            sess.run(init)
        else:
            # logger.info('Restore model from last crnn check point{:s}'.format(weights_path))
            # init = tf.global_variables_initializer()
            # sess.run(init)
            # restore_saver = tf.train.Saver(var_list=restore_variable_list)
            # restore_saver.restore(sess=sess, save_path=weights_path)
            logger.info('Restore model from last crnn check point{:s}'.format(FLAGS.weights_path))
            saver.restore(sess=sess, save_path=FLAGS.weights_path)

        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(sess=sess, coord=coord)

        for epoch in range(train_epochs):
            _, c, seq_distance, preds, gt_labels = sess.run(
                [optimizer, cost, sequence_dist, decoded, input_labels],
                feed_dict={phase_tensor: 'train'})

            # calculate the precision
            preds = decoder.sparse_tensor_to_str(preds[0])
            gt_labels = decoder.sparse_tensor_to_str(gt_labels)

            accuracy = []

            for index, gt_label in enumerate(gt_labels):
                pred = preds[index]
                totol_count = len(gt_label)
                correct_count = 0
                try:
                    for i, tmp in enumerate(gt_label):
                        if tmp == pred[i]:
                            correct_count += 1
                except IndexError:
                    continue
                finally:
                    try:
                        accuracy.append(correct_count / totol_count)
                    except ZeroDivisionError:
                        if len(pred) == 0:
                            accuracy.append(1)
                        else:
                            accuracy.append(0)
            accuracy = np.mean(np.array(accuracy).astype(np.float32), axis=0)

            train_summary = sess.run(train_summary_op_merge,
                                     feed_dict={accuracy_tensor: accuracy,
                                                phase_tensor: 'train'})
            summary_writer.add_summary(summary=train_summary, global_step=epoch)

            if epoch % config.cfg.TRAIN.DISPLAY_STEP == 0:

                logger.info('Epoch: {:d} cost= {:9f} seq distance= {:9f} train accuracy= {:9f}'.format(
                    epoch + 1, c, seq_distance, accuracy))

            # if epoch % config.cfg.TRAIN.VAL_STEP == 0:
            #     inputdata_value = sess.run(inputdata_val)
            #     val_c, val_seq, val_preds, val_gt_labels = sess.run([
            #         cost, sequence_dist, decoded, input_labels_val],
            #         feed_dict={phase_tensor: 'test',
            #                    input_tensor: inputdata_value})
            #
            #     preds_val = decoder.sparse_tensor_to_str(val_preds[0])
            #     gt_labels_val = decoder.sparse_tensor_to_str(val_gt_labels)
            #
            #     accuracy_val = []
            #
            #     for index, gt_label in enumerate(gt_labels_val):
            #         pred = preds_val[index]
            #         totol_count = len(gt_label)
            #         correct_count = 0
            #         try:
            #             for i, tmp in enumerate(gt_label):
            #                 if tmp == pred[i]:
            #                     correct_count += 1
            #         except IndexError:
            #             continue
            #         finally:
            #             try:
            #                 accuracy_val.append(correct_count / totol_count)
            #             except ZeroDivisionError:
            #                 if len(pred) == 0:
            #                     accuracy_val.append(1)
            #                 else:
            #                     accuracy_val.append(0)
            #
            #     accuracy_val = np.mean(np.array(accuracy_val).astype(np.float32), axis=0)
            #
            #     test_summary = sess.run(test_summary_op_merge,
            #                             feed_dict={accuracy_tensor: accuracy_val,
            #                                        phase_tensor: 'test',
            #                                        input_tensor: inputdata_value})
            #     summary_writer.add_summary(summary=test_summary, global_step=epoch)
            #
            #     logger.info('Epoch: {:d} val_cost= {:9f} val_seq_distance= {:9f} val_accuracy= {:9f}'.format(
            #         epoch + 1, val_c, val_seq, accuracy_val))

            if epoch % 500 == 0:
                saver.save(sess=sess, save_path=model_save_path, global_step=epoch)

        coord.request_stop()
        coord.join(threads=threads)

    sess.close()

    return

def main(_):
    train_shadownet()

if __name__ == '__main__':
    # init args
    # args = init_args()

    #if not ops.exists(args.dataset_dir):
    #    raise ValueError('{:s} doesn\'t exist'.format(args.dataset_dir))

    #train_shadownet(args.dataset_dir, args.weights_path)

    # if args.weights_path is not None and 'two_stage' in args.weights_path:
    #     train_shadownet(args.dataset_dir, args.weights_path, restore_from_cnn_subnet_work=False)
    # elif args.weights_path is not None and 'cnnsub' in args.weights_path:
    #     train_shadownet(args.dataset_dir, args.weights_path, restore_from_cnn_subnet_work=True)
    # else:
    #     train_shadownet(args.dataset_dir)
    tf.app.run()
    print('Done')
