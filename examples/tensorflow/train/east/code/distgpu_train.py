import time
import os
import functools
import itertools
import numpy as np
import tensorflow as tf
from tensorflow.contrib import slim

import six
from six.moves import xrange  # pylint: disable=redefined-builtin

import icdar_dataset

from uaitrain.arch.tensorflow import uflag

tf.app.flags.DEFINE_integer('input_size', 512, '')
tf.app.flags.DEFINE_integer('batch_size', 128, '')
tf.app.flags.DEFINE_integer('num_readers', 16, '')
tf.app.flags.DEFINE_float('learning_rate', 0.0001, '')
tf.app.flags.DEFINE_integer('max_steps', 100000, '')
tf.app.flags.DEFINE_float('moving_average_decay', 0.997, '')
tf.app.flags.DEFINE_boolean('restore', False, 'whether to resotre from checkpoint')
tf.app.flags.DEFINE_integer('save_checkpoint_steps', 1000, '')
tf.app.flags.DEFINE_integer('save_summary_steps', 100, '')
tf.app.flags.DEFINE_string('pretrained_model_path', None, '')
tf.app.flags.DEFINE_integer('num_intra_threads', 0, '')
tf.app.flags.DEFINE_string('train_dir', 'tfrecords', '')
tf.app.flags.DEFINE_boolean('sync', False, '')
tf.app.flags.DEFINE_integer('decay_steps', 10000, '')
tf.app.flags.DEFINE_float('decay_rate', 0.94, '')

import model

from tensorflow.core.framework import node_def_pb2
from tensorflow.python.framework import device as pydev
from tensorflow.python.training import device_setter

FLAGS = tf.app.flags.FLAGS

from tensorflow.python.training import device_setter

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

def _tower_fn(is_training, images, score_maps, geo_maps, training_masks, reuse_variables=None):
    # Build inference graph
    with tf.variable_scope(tf.get_variable_scope(), reuse=reuse_variables):
        f_score, f_geometry = model.model(images, is_training=is_training)

    model_loss = model.loss(score_maps, f_score,
                            geo_maps, f_geometry,
                            training_masks)
    total_loss = tf.add_n([model_loss] + tf.get_collection(tf.GraphKeys.REGULARIZATION_LOSSES))

    # add summary
    summaries = None
    if reuse_variables is None:
        image_sum = tf.summary.image('input', images)
        score_sum = tf.summary.image('score_map', score_maps)
        f_score_sum = tf.summary.image('score_map_pred', f_score * 255)
        geo_sum = tf.summary.image('geo_map_0', geo_maps[:, :, :, 0:1])
        f_geo_sum = tf.summary.image('geo_map_0_pred', f_geometry[:, :, :, 0:1])
        mask_sum = tf.summary.image('training_masks', training_masks)
        loss1_sum = tf.summary.scalar('model_loss', model_loss)
        loss_sum = tf.summary.scalar('total_loss', total_loss)
        summaries = [image_sum, score_sum, f_score_sum, geo_sum, f_geo_sum, mask_sum, loss1_sum, loss_sum]

    model_params = tf.trainable_variables()
    tower_grad = tf.gradients(total_loss, model_params)

    return total_loss, zip(tower_grad, model_params), summaries

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
        four
    """
    with tf.device('/cpu:0'):
        use_distortion = subset == 'train' and use_distortion_for_training
        dataset = icdar_dataset.EastDataSet(data_dir, batch_size, subset, use_distortion)
        image_batch, score_map_batch, geo_map_batch, training_mask_batch = dataset.make_batch(batch_size)

        if num_shards <= 1:
            # No GPU available or only 1 GPU.
            num_shards = 1

        feature_shards = tf.split(image_batch, num_shards)
        score_map_shards = tf.split(score_map_batch, num_shards)
        geo_map_shards = tf.split(geo_map_batch, num_shards)
        training_mask_shards = tf.split(training_mask_batch, num_shards)

        return feature_shards, [score_map_shards, geo_map_shards, training_mask_shards]

def get_mode_fn(num_gpus, variable_strategy, num_workers):
    """Returns a function that will build shadownet model."""

    def _mode_fun(features, labels, mode, params):
        is_training = (mode == tf.estimator.ModeKeys.TRAIN)

        tower_features = features
        tower_score_maps = labels[0]
        tower_geo_maps = labels[1]
        tower_training_masks = labels[2]
        tower_losses = []
        tower_gradvars = []
        tower_summaries = []

        num_devices = FLAGS.num_gpus
        device_type = 'gpu'

        reuse_variables = None
        for i in range(num_devices):
            worker_device = '/{}:{}'.format(device_type, i)
            device_setter = local_device_setter(worker_device=worker_device)

            with tf.name_scope('tower_%d' % i) as name_scope:
                with tf.device(device_setter):
                    total_loss, gradvars, summaries = _tower_fn(
                            is_training, 
                            tower_features[i],
                            tower_score_maps[i],
                            tower_geo_maps[i],
                            tower_training_masks[i],
                            reuse_variables)
                    tower_losses.append(total_loss)
                    tower_gradvars.append(gradvars)
                    tower_summaries.append(summaries)
                    reuse_variables = True

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

        if FLAGS.pretrained_model_path is not None:
            tf.train.init_from_checkpoint(FLAGS.pretrained_model_path, {"resnet_v1_50/":"resnet_v1_50/"})
        # restore only once
        FLAGS.pretrained_model_path = None

        # Device that runs the ops to apply global gradient updates.
        consolidation_device = '/gpu:0' if variable_strategy == 'GPU' else '/cpu:0'
        with tf.device(consolidation_device):
            global_step = tf.train.get_global_step()
            starter_learning_rate = FLAGS.learning_rate

            learning_rate = tf.train.exponential_decay(starter_learning_rate, global_step,
                                                       FLAGS.decay_steps, FLAGS.decay_rate,
                                                       staircase=True)
            loss = tf.reduce_mean(tower_losses, name='loss')

            tensors_to_log = {'global_step': global_step, 'learning_rate': learning_rate, 'loss': loss}
            logging_hook = tf.train.LoggingTensorHook(
                tensors=tensors_to_log, every_n_iter=10)

            summary_hook = tf.train.SummarySaverHook(
                save_steps=10,
                output_dir='/data/output/',
                summary_op=tower_summaries[0])
            train_hooks = [logging_hook, summary_hook]

            optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
            if FLAGS.sync:
                optimizer = tf.train.SyncReplicasOptimizer(
                    optimizer, replicas_to_aggregate=num_workers)

                sync_replicas_hook = optimizer.make_session_run_hook(params.is_chief)
                train_hooks.append(sync_replicas_hook)

            # save moving average
            variable_averages = tf.train.ExponentialMovingAverage(
                FLAGS.moving_average_decay, global_step)
            variables_averages_op = variable_averages.apply(tf.trainable_variables())

            # Create single grouped train op
            train_op = [
                optimizer.apply_gradients(
                    gradvars, global_step=tf.train.get_global_step()),
                variables_averages_op
            ]
            train_op.extend(update_ops)
            train_op = tf.group(*train_op)

        return tf.estimator.EstimatorSpec(
            mode=mode,
            loss=loss,
            train_op=train_op,
            training_hooks=train_hooks)
    return _mode_fun

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
            batch_size=FLAGS.batch_size,
            use_distortion_for_training=use_distortion_for_training)

        eval_input_fn = functools.partial(
            input_fn,
            data_dir,
            subset='validation',
            batch_size=FLAGS.batch_size,
            num_shards=num_gpus)

        train_steps = FLAGS.max_steps
        eval_steps = 900 // FLAGS.batch_size

        variable_strategy = 'CPU'
        classifier = tf.estimator.Estimator(
            model_fn=get_mode_fn(num_gpus,
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

def main(argv=None):
    num_gpus = FLAGS.num_gpus
    log_device_placement = False
    data_dir = FLAGS.data_dir
    output_dir = FLAGS.output_dir
    train_dir = FLAGS.train_dir

    # The env variable is on deprecation path, default is set to off.
    os.environ['TF_SYNC_ON_FINISH'] = '1'
    os.environ['TF_ENABLE_WINOGRAD_NONFUSED'] = '1'
    data_dir = os.path.join(data_dir, train_dir)
    tf.logging.set_verbosity(tf.logging.INFO)

    # Session configuration.
    sess_config = tf.ConfigProto(
        allow_soft_placement=True,
        log_device_placement=log_device_placement,
        intra_op_parallelism_threads=FLAGS.num_intra_threads,
        gpu_options=tf.GPUOptions(force_gpu_compatible=True))
    config = tf.contrib.learn.RunConfig(session_config=sess_config, model_dir=output_dir)

    tf.contrib.learn.learn_runner.run(
        get_experiment_fn(data_dir, num_gpus),
        run_config=config,
        hparams=tf.contrib.training.HParams(
            is_chief=config.is_chief))

if __name__ == '__main__':
    tf.app.run()