"""
Train shadow net script
"""
import argparse
import functools
import itertools
import os
import os.path as ops
import sys
import time

import numpy as np
import tensorflow as tf
import pprint
import shadownet

import six
from six.moves import xrange  # pylint: disable=redefined-builtin

sys.path.append('/data/')

from crnn_model import crnn_model
from local_utils import data_utils, log_utils, tensorboard_vis_summary
from global_configuration import config
from uaitrain.arch.tensorflow import uflag
from typing import List

from tensorflow.core.framework import node_def_pb2
from tensorflow.python.framework import device as pydev
from tensorflow.python.training import device_setter

tf.app.flags.DEFINE_string('dataset_dir','/data/data/tfrecords','data path')
tf.app.flags.DEFINE_string('weights_path',None,'weight path')
FLAGS = tf.app.flags.FLAGS

logger = log_utils.init_logger()

def local_device_setter(num_devices=1,
                        ps_device_type='cpu',
                        worker_device='/cpu:0',
                        ps_ops=None,
                        ps_strategy=None):
    if ps_ops == None:
        ps_ops = ['Variable', 'VariableV2', 'VarHandleOp']

    if ps_strategy is None:
        ps_strategy = device_setter._RoundRobinStrategy(num_devices)
    if not six.callable(ps_strategy):
        raise TypeError("ps_strategy must be callable")

    def _local_device_chooser(op):
        current_device = pydev.DeviceSpec.from_string(op.device or "")

        node_def = op if isinstance(op, node_def_pb2.NodeDef) else op.node_def
        if node_def.op in ps_ops:
            ps_device_spec = pydev.DeviceSpec.from_string(
                  '/{}:{}'.format(ps_device_type, ps_strategy(op)))

            ps_device_spec.merge_from(current_device)
            return ps_device_spec.to_string()
        else:
            worker_device_spec = pydev.DeviceSpec.from_string(worker_device or "")
            worker_device_spec.merge_from(current_device)
            return worker_device_spec.to_string()
    return _local_device_chooser

def get_words_from_chars(characters_list: List[str], sequence_lengths: List[int], name='chars_conversion'):
    with tf.name_scope(name=name):
        def join_charcaters_fn(coords):
            return tf.reduce_join(characters_list[coords[0]:coords[1]])

        def coords_several_sequences():
            end_coords = tf.cumsum(sequence_lengths)
            start_coords = tf.concat([[0], end_coords[:-1]], axis=0)
            coords = tf.stack([start_coords, end_coords], axis=1)
            coords = tf.cast(coords, dtype=tf.int32)
            return tf.map_fn(join_charcaters_fn, coords, dtype=tf.string)

        def coords_single_sequence():
            return tf.reduce_join(characters_list, keep_dims=True)

        words = tf.cond(tf.shape(sequence_lengths)[0] > 1,
                        true_fn=lambda: coords_several_sequences(),
                        false_fn=lambda: coords_single_sequence())

        return words

def get_shadownet_fn(num_gpus, variable_strategy, num_workers):
    """Returns a function that will build shadownet model."""

    def _shadownet_fun(features, labels, mode, params):
        is_training = (mode == tf.estimator.ModeKeys.TRAIN)

        tower_features = features
        tower_labels = labels
        tower_losses = []
        tower_gradvars = []
        tower_preds = []
        tower_tensor_dict = []
        tower_seq_len = []

        num_devices = num_gpus
        device_type = 'gpu'
        tower_batch_size = int(params.batch_size / num_devices)

        for i in range(num_devices):
            worker_device = '/{}:{}'.format(device_type, i)
            device_setter = local_device_setter(worker_device=worker_device)

            with tf.variable_scope('shadownet', reuse=bool(i != 0)):
                with tf.name_scope('tower_%d' % i) as name_scope:
                    with tf.device(device_setter):
                        loss, gradvars, preds, tensor_dict, seq_len = _tower_fn(
                            is_training, tower_features[i], tower_labels[i], tower_batch_size, params.l_size)
                        tower_losses.append(loss)
                        tower_gradvars.append(gradvars)
                        tower_preds.append(preds)
                        tower_tensor_dict.append(tensor_dict)
                        tower_seq_len.append(seq_len)

                        if i == 0:
                            # Only trigger batch_norm moving mean and variance update from
                            # the 1st tower. Ideally, we should grab the updates from all
                            # towers but these stats accumulate extremely fast so we can
                            # ignore the other stats from the other towers without
                            # significant detriment.
                            update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS,
                                                           name_scope)
        # Now compute global loss and gradients.
        gradvars = []
        with tf.name_scope('gradient_averaging'):
            all_grads = {}
            for grad, var in itertools.chain(*tower_gradvars):
                if grad is not None:
                    all_grads.setdefault(var, []).append(grad)
            for var, grads in six.iteritems(all_grads):
                # Average gradients on the same device as the variables
                with tf.device(var.device):
                    if len(grads) == 1:
                        avg_grad = grads[0]
                    else:
                        avg_grad = tf.multiply(tf.add_n(grads), 1. / len(grads))
                gradvars.append((avg_grad, var))

        # Device that runs the ops to apply global gradient updates.
        consolidation_device = '/gpu:0' if variable_strategy == 'GPU' else '/cpu:0'
        with tf.device(consolidation_device):
            global_step = tf.train.get_global_step()
            starter_learning_rate = params.learning_rate
            learning_rate = tf.train.exponential_decay(starter_learning_rate, global_step,
                                                       params.decay_steps, params.decay_rate,
                                                       staircase=True)
            loss = tf.reduce_mean(tower_losses, name='loss')
            decoded, log_prob = tf.nn.ctc_beam_search_decoder(tower_preds[0],
                                                              tower_seq_len[0]*np.ones(tower_batch_size),
                                                              merge_repeated=False)
            sequence_dist = tf.reduce_mean(tf.edit_distance(tf.cast(decoded[0], tf.int32), tower_labels[0]))

            sequence_lengths_pred = tf.bincount(tf.cast(decoded[0].indices[:, 0], tf.int32),
                                                minlength=tf.shape(tower_labels[0])[1])
            label_lengths_pred = tf.bincount(tf.cast(labels[0].indices[:, 0], tf.int32),
                                                minlength=tf.shape(tower_labels[0])[1])

            tensors_to_log = {'global_step': global_step, 'learning_rate': learning_rate, 'loss': loss}
            dist_to_log = {'global_step': global_step,
                'learning_rate': learning_rate,
                'loss': loss,
                'train_seq_dist': sequence_dist,
                'sequence_lengths_pred': sequence_lengths_pred,
                'label_lengths_pred': label_lengths_pred}

            logging_hook = tf.train.LoggingTensorHook(
                tensors=tensors_to_log, every_n_iter=10)
            dist_hook = tf.train.LoggingTensorHook(
                tensors=dist_to_log, every_n_iter=1000) 
            train_hooks = [logging_hook, dist_hook]

            seq_dist_sum = tf.summary.scalar(name='Seq_Dist', tensor=sequence_dist)
            lr_sum = tf.summary.scalar(name='Learning_rate', tensor=learning_rate)
            summaries = [seq_dist_sum, lr_sum]

            summary_hook = tf.train.SummarySaverHook(
                save_steps=1000,
                output_dir='/data/output/',
                summary_op=summaries)

            optimizer = tf.train.AdadeltaOptimizer(learning_rate=learning_rate)
            if params.sync:
                optimizer = tf.train.SyncReplicasOptimizer(
                    optimizer, replicas_to_aggregate=num_workers)

                sync_replicas_hook = optimizer.make_session_run_hook(params.is_chief)
                train_hooks.append(sync_replicas_hook)

            # Create single grouped train op
            train_op = [
                optimizer.apply_gradients(
                    gradvars, global_step=tf.train.get_global_step())
            ]
            train_op.extend(update_ops)
            train_op = tf.group(*train_op)

        return tf.estimator.EstimatorSpec(
            mode=mode,
            loss=loss,
            train_op=train_op,
            training_hooks=train_hooks)
    return _shadownet_fun

def _tower_fn(is_training, feature, label, batch_size, l_size):
    seq_len=l_size
    shadownet = crnn_model.ShadowNet(phase='Train', hidden_nums=256, layers_nums=2, seq_length=seq_len,                                                        
                                     num_classes=config.cfg.TRAIN.CLASSES_NUMS, rnn_cell_type='lstm')                                                          
    
    imgs = tf.image.resize_images(feature, (32, l_size*4), method=0)                                                                                           
    input_imgs = tf.cast(x=imgs, dtype=tf.float32)                                                                                                             
    
    with tf.variable_scope('shadow', reuse=False):
        net_out, tensor_dict = shadownet.build_shadownet(inputdata=input_imgs)                                                                                 
    
    cost = tf.reduce_mean(tf.nn.ctc_loss(labels=label, inputs=net_out,
                                         sequence_length=seq_len*np.ones(batch_size)))                                                                         
    
    #lstm l2 normalization loss
    lstm_tv = tf.trainable_variables(scope='LSTMLayers')                                                                                                       
    r_lambda = 0.001
    regularization_cost = r_lambda * tf.reduce_sum([tf.nn.l2_loss(v) for v in lstm_tv])                                                                        
    cost = cost + regularization_cost                                                                                                                          
    
    model_params = tf.trainable_variables()
    tower_grad = tf.gradients(cost, model_params)                                                                                                              
    
    return cost, zip(tower_grad, model_params), net_out, tensor_dict, seq_len

def input_fn(data_dir,
            subset,
            num_shards, 
            batch_size,
            use_distortion_for_training=True):
    """Create input graph for model.

    Args:
      data_dir: Directory where TFRecords representing the dataset are located.
      subset: one of 'train', 'validate' and 'eval'.
      num_shards: num of towers participating in data-parallel training.
      batch_size: total batch size for training to be divided by the number of
      shards.
      use_distortion_for_training: True to use distortions.
    Returns:
      three
    """
    with tf.device('/cpu:0'):
        use_distortion = subset == 'train' and use_distortion_for_training
        dataset = shadownet.ShadownetDataSet(data_dir, subset, use_distortion)
        inputdata, input_labels = dataset.make_batch(batch_size)

        if num_shards <= 1:
            # No GPU available or only 1 GPU.
            num_shards = 1

        feature_shards = tf.split(inputdata, num_shards)
        label_shards = tf.sparse_split(sp_input=input_labels, num_split=num_shards, axis=0)
        return feature_shards, label_shards

def get_experiment_fn(data_dir,
                      num_gpus,
                      use_distortion_for_training=True):
    def _experiment_fn(run_config, hparams):
        """Returns an Experiment."""
        # Create estimator.
        train_input_fn = functools.partial(
            input_fn,
            data_dir,
            subset='train',
            num_shards=num_gpus,
            batch_size=hparams.batch_size,
            use_distortion_for_training=use_distortion_for_training)

        eval_input_fn = functools.partial(
            input_fn,
            data_dir,
            subset='validation',
            batch_size=hparams.batch_size,
            num_shards=num_gpus)

        train_steps = hparams.steps
        eval_steps = 2048 // hparams.batch_size

        variable_strategy = 'CPU'
        classifier = tf.estimator.Estimator(
            model_fn=get_shadownet_fn(num_gpus,
                                  variable_strategy,
                                  run_config.num_worker_replicas or 1),
            config=run_config,
            params=hparams)

        # Create experiment.
        return tf.contrib.learn.Experiment(
                classifier,
                train_input_fn=train_input_fn,
                eval_input_fn=eval_input_fn,
                train_steps=train_steps,
                eval_steps=eval_steps,
                min_eval_frequency=100)

    return _experiment_fn

def main(num_gpus, log_device_placement, num_intra_threads, data_dir, output_dir, tfrecord_dir, **hparams):
    # The env variable is on deprecation path, default is set to off.
    os.environ['TF_SYNC_ON_FINISH'] = '0'
    os.environ['TF_ENABLE_WINOGRAD_NONFUSED'] = '1'
    data_dir = os.path.join(data_dir, tfrecord_dir)

    # Session configuration.
    sess_config = tf.ConfigProto(
        allow_soft_placement=True,
        log_device_placement=log_device_placement,
        intra_op_parallelism_threads=num_intra_threads,
        gpu_options=tf.GPUOptions(force_gpu_compatible=True))
    config = tf.contrib.learn.RunConfig(session_config=sess_config, model_dir=output_dir)

    tf.contrib.learn.learn_runner.run(
        get_experiment_fn(data_dir, num_gpus),
        run_config=config,
        hparams=tf.contrib.training.HParams(
            is_chief=config.is_chief,
            **hparams))

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
    parser = argparse.ArgumentParser()

    parser.add_argument(
      '--num_gpus',
      type=int,
      default=1,
      help='UAI-SDK related. The number of gpus used.')
    parser.add_argument(
      '--log-device-placement',
      action='store_true',
      default=False,
      help='Whether to log device placement.')

    parser.add_argument(
      '--num-intra-threads',
      type=int,
      default=0,
      help="""\
      Number of threads to use for intra-op parallelism. When training on CPU
      set to 0 to have the system pick the appropriate number or alternatively
      set it to the number of physical CPU cores.\
      """)
    parser.add_argument(
      '--num-inter-threads',
      type=int,
      default=0,
      help="""\
      Number of threads to use for inter-op parallelism. If set to 0, the
      system will pick an appropriate number.\
      """)
    parser.add_argument(
      '--sync',
      action='store_true',
      default=False,
      help="""\
      If present when running in a distributed environment will run on sync mode.\
      """)
    parser.add_argument(
      '--work_dir',
      type=str,
      default='/data/',
      help='UAI SDK related.')
    parser.add_argument(
      '--data_dir',
      type=str,
      required=True,
      help='UAI-SDK related. The directory where the CIFAR-10 input data is stored.')
    parser.add_argument(
      '--output_dir',
      type=str,
      required=True,
      help='UAI-SDK related. The directory where the model will be stored.')
    parser.add_argument(
      '--log_dir',
      type=str,
      default='/data/data/',
      help='UAI SDK related.')
    parser.add_argument(
      '--l_size',
      type=int,
      default=10,
      help="""l_batch_label, how many labels CNN net work will output into LSTM""")
    parser.add_argument(
      '--learning_rate',
      type=float,
      default=0.1)
    parser.add_argument(
      '--decay_rate',
      type=float,
      default=0.1)
    parser.add_argument(
      '--decay_steps',
      type=int,
      default=40000)
    parser.add_argument(
      '--steps',
      type=int,
      default=200000)
    parser.add_argument(
      '--batch_size',
      type=int,
      default=512)
    parser.add_argument(
      '--tfrecord_dir',
      type=str,
      default='tfrecords')

    args = parser.parse_args()
    main(**vars(args))
    print('Done')