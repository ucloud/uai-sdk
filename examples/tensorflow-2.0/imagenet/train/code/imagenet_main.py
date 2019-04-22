# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""ResNet model for classifying images from Imagenet dataset.

Support single-host training with one or multiple devices.

ResNet as proposed in:
Kaiming He, Xiangyu Zhang, Shaoqing Ren, Jian Sun
Deep Residual Learning for Image Recognition. arXiv:1512.03385

"""
from __future__ import division
from __future__ import print_function

import argparse
import functools
import itertools
import os
import json

import imagenet
import imagenet_utils
import resnet_model
import numpy as np
import six
from six.moves import xrange  # pylint: disable=redefined-builtin
import tensorflow as tf

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.INFO)

_NUM_IMAGES = {
    'train': 1281167,
    'validation': 50000,
}

def get_model_fn(num_gpus, variable_strategy, num_workers):
  """Returns a function that will build the resnet model."""

  def _resnet_model_fn(features, labels, mode, params):
    """Resnet model body.

    Support single host, one or more GPU training. Parameter distribution can
    be either one of the following scheme.
    1. CPU is the parameter server and manages gradient updates.
    2. Parameters are distributed evenly across all GPUs, and the first GPU
       manages gradient updates.

    Args:
      features: a list of tensors, one for each tower
      labels: a list of tensors, one for each tower
      mode: ModeKeys.TRAIN or EVAL
      params: Hyperparameters suitable for tuning
    Returns:
      A EstimatorSpec object.
    """
    is_training = (mode == tf.estimator.ModeKeys.TRAIN)
    weight_decay = params['weight_decay']
    momentum = params['momentum']

    # channels first (NCHW) is normally optimal on GPU and channels last (NHWC)
    # on CPU. The exception is Intel MKL on CPU which is optimal with
    # channels_last.
    data_format = params['data_format']
    if not data_format:
      if num_gpus == 0:
        data_format = 'channels_last'
      else:
        data_format = 'channels_first'

    if num_gpus == 0:
      num_devices = 1
      device_type = 'cpu'
    else:
      num_devices = num_gpus
      device_type = 'gpu'

    loss, preds = _tower_fn(
        is_training, weight_decay, features, labels,
        data_format, params['resnet_size'], params['batch_norm_decay'],
        params['batch_norm_epsilon'])

    batches_per_epoch = _NUM_IMAGES['train'] / (params['train_batch_size'] * num_workers)

    boundaries = [
        int(batches_per_epoch * epoch) for epoch in [30, 60, 80, 90]]
    staged_lr = [params['learning_rate'] * decay for decay in [1, 0.1, 0.01, 1e-3, 1e-4]]

    learning_rate = tf.compat.v1.train.piecewise_constant(tf.compat.v1.train.get_global_step(),
                                                  boundaries, staged_lr)
    tf.identity(learning_rate, name='learning_rate')
    lr_s = tf.compat.v1.summary.scalar('learning_rate', learning_rate)

    loss = tf.reduce_mean(loss, name='loss')

    examples_sec_hook = imagenet_utils.ExamplesPerSecondHook(
        params['train_batch_size'], every_n_steps=10)

    optimizer = tf.compat.v1.train.MomentumOptimizer(
        learning_rate=learning_rate, momentum=momentum)
    train_op = optimizer.minimize(loss, global_step=tf.compat.v1.train.get_global_step())

    predictions = {
        'classes': preds['classes'],
        'probabilities': preds['probabilities'],
        'top5_class': preds['top5_classes'],
    }

    stacked_labels = labels
    accuracy = tf.compat.v1.metrics.accuracy(stacked_labels, predictions['classes'])
    #accuracy_5 = tf.compat.v1.metrics.recall_at_top_k(tf.cast(stacked_labels, tf.int64), predictions['top5_class'], k=5)

    acc_s = tf.compat.v1.summary.scalar('train_accuracy', accuracy[1])
    tensors_to_log = {'learning_rate': learning_rate, 'loss': loss, 'acc': accuracy[1]}
    logging_hook = tf.estimator.LoggingTensorHook(
        tensors=tensors_to_log, every_n_secs=10)

    summary_op = [acc_s, lr_s]
    summary_hook = tf.estimator.SummarySaverHook(
                save_steps=100,
                summary_op=summary_op)

    train_hooks = [logging_hook, examples_sec_hook, summary_hook]

    metrics = None
    if (mode ==  tf.estimator.ModeKeys.EVAL):
      metrics = {
        'accuracy': accuracy,
        #'accuracy_5': accuracy_5,
      }

    return tf.estimator.EstimatorSpec(
        mode=mode,
        predictions=predictions,
        loss=loss,
        train_op=train_op,
        training_hooks=train_hooks,
        eval_metric_ops=metrics)

  return _resnet_model_fn


def _tower_fn(is_training, weight_decay, feature, label, data_format,
              resnet_size, batch_norm_decay, batch_norm_epsilon):
  """Build computation tower (Resnet).

  Args:
    is_training: true if is training graph.
    weight_decay: weight regularization strength, a float.
    feature: a Tensor.
    label: a Tensor.
    data_format: channels_last (NHWC) or channels_first (NCHW).
    num_layers: number of layers, an int.
    batch_norm_decay: decay for batch normalization, a float.
    batch_norm_epsilon: epsilon for batch normalization, a float.

  Returns:
    A tuple with the loss for the tower, the gradients and parameters, and
    predictions.

  """
  network = resnet_model.imagenet_resnet_v2(resnet_size, 1000 + 1, data_format)
  logits = network(feature, is_training=is_training)
  _, top_k_indices = tf.nn.top_k(logits,  k=5)
  tower_pred = {
      'classes': tf.argmax(input=logits, axis=1),
      'probabilities': tf.nn.softmax(logits),
      'top5_classes': top_k_indices
  }

  tower_loss = tf.compat.v1.losses.sparse_softmax_cross_entropy(
      logits=logits, labels=label)
  tower_loss = tf.reduce_mean(tower_loss)

  model_params = tf.compat.v1.trainable_variables()
  tower_loss += weight_decay * tf.add_n(
      [tf.nn.l2_loss(v) for v in model_params])

  #tower_grad = tf.gradients(tower_loss, model_params)

  return tower_loss, tower_pred


def input_fn(data_dir,
             subset,
             num_gpus,
             batch_size,
             num_epochs=1,
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
    two lists of tensors for features and labels, each of num_shards length.
  """
  with tf.device('/cpu:0'):
    use_distortion = subset == 'train' and use_distortion_for_training
    dataset = imagenet.ImagenetDataSet(data_dir, subset, use_distortion)

    print(num_gpus)
    dataset = dataset.make_dataset(batch_size, 
        is_training=(subset == 'train'), 
        num_shards=num_gpus, 
        num_epochs=num_epochs)
    return dataset

def main(output_dir, data_dir, num_gpus, train_epochs, epochs_per_eval, variable_strategy,
         use_distortion_for_training, log_device_placement, num_intra_threads,
         **hparams):
  print('num of gpus:')
  print(num_gpus)
  # The env variable is on deprecation path, default is set to off.
  os.environ['TF_SYNC_ON_FINISH'] = '0'
  os.environ['TF_ENABLE_WINOGRAD_NONFUSED'] = '1'

  is_dist = False
  # handle dist traning info
  if 'TF_CONFIG' in os.environ:
    is_dist = True
    tf_dist_conf = os.environ['TF_CONFIG']
    conf = json.loads(tf_dist_conf)
    if conf['task']['type'] == 'ps':
      is_ps = True
    else:
      is_ps = False

    '''
    if is_ps:
      if conf['task']['index'] == '0' or conf['task']['index'] == 0:
        conf['cluster']['evaluator'] = [conf['cluster']['ps'][0]]
        conf['task']['type'] = 'evaluator'
        is_ps = False
        print('ps act as evaluator')
    '''

    if conf['task']['type'] == 'master':
      conf['task']['type'] = 'chief'

    conf['cluster']['chief'] = conf['cluster']['master']
    del conf['cluster']['master']

    # If you need evaluator, we can change the role of last worker
    n_workers = len(conf['cluster']['worker'])
    last_worker = conf['cluster']['worker'][-1]
    conf['cluster']['worker'] = conf['cluster']['worker'][0:-1]
    conf['cluster']['evaluator'] = [last_worker]
    if conf['task']['type'] == 'worker' and conf['task']['index'] == (n_workers - 1):
      conf['task']['index'] = 0
      conf['task']['type'] ='evaluator'

    print(conf)
    os.environ['TF_CONFIG'] = json.dumps(conf)
    
  if is_dist:
    if is_ps:    
      # dummy call, no usage for MultiWorkerMirroredStrategy() in dist train
      distribution = tf.distribute.experimental.ParameterServerStrategy()
    else:
      distribution = tf.distribute.experimental.MultiWorkerMirroredStrategy()
  else:
    distribution = tf.distribute.MirroredStrategy()

  # Session configuration.
  sess_config = tf.compat.v1.ConfigProto(
      allow_soft_placement=True,
      log_device_placement=log_device_placement,
      intra_op_parallelism_threads=num_intra_threads,
      gpu_options=tf.compat.v1.GPUOptions(force_gpu_compatible=True))
  config = tf.estimator.RunConfig(model_dir=output_dir,
      save_checkpoints_secs=3600,
      train_distribute=distribution,
      eval_distribute=distribution,
      session_config=sess_config)

  hparams['is_chief']=config.is_chief

  resnet_classifier = tf.estimator.Estimator(
      model_fn=get_model_fn(num_gpus, variable_strategy, config.num_worker_replicas or 1),
      config=config,
      params=hparams)

  num_workers = (config.num_worker_replicas or 1)
  batches_per_epoch = _NUM_IMAGES['train'] / (hparams['train_batch_size'] * num_workers)
  max_steps = train_epochs * batches_per_epoch

  batch_size = hparams['train_batch_size']
  train_spec = tf.estimator.TrainSpec(input_fn=lambda: input_fn(
            data_dir,
            subset='train',
            num_gpus=num_gpus,
            batch_size=batch_size,
            use_distortion_for_training=use_distortion_for_training,
            num_epochs=train_epochs),
            max_steps=max_steps)

  eval_spec = tf.estimator.EvalSpec(input_fn=lambda: input_fn(
          data_dir,
          subset='validation',
          batch_size=hparams['eval_batch_size'],
          num_gpus=num_gpus),
          steps=500,
          start_delay_secs=0)

  tf.estimator.train_and_evaluate(
    resnet_classifier,
    train_spec,
    eval_spec)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  
  """UAI SDK use data_dir output_dir and num_gpus to transfer system specific data
  """
  parser.add_argument(
      '--data_dir',
      type=str,
      required=True,
      help='UAI SDK related. The directory where the imagenet input data is stored.')
  parser.add_argument(
      '--output_dir',
      type=str,
      required=True,
      help='UAI SDK related. The directory where the model will be stored.')
  parser.add_argument(
      '--variable-strategy',
      choices=['CPU', 'GPU'],
      type=str,
      default='CPU',
      help='Where to locate variable operations')
  parser.add_argument(
      '--num_gpus',
      type=int,
      default=1,
      help='UAI SDK related. The number of gpus used.')
  parser.add_argument(
    '--resnet_size', type=int, default=50, choices=[18, 34, 50, 101, 152, 200],
    help='The size of the ResNet model to use.')
  parser.add_argument(
      '--num-layers',
      type=int,
      default=44,
      help='The number of layers of the model.')
  parser.add_argument(
      '--train-epochs',
      type=int,
      default=100,
      help='The number of epochs to use for training.')
  parser.add_argument(
      '--epochs_per_eval', 
      type=int, 
      default=1,
      help='The number of training epochs to run between evaluations.')
  parser.add_argument(
      '--train-batch-size',
      type=int,
      default=128,
      help='Batch size for training.')
  parser.add_argument(
      '--eval-batch-size',
      type=int,
      default=100,
      help='Batch size for validation.')
  parser.add_argument(
      '--momentum',
      type=float,
      default=0.9,
      help='Momentum for MomentumOptimizer.')
  parser.add_argument(
      '--weight-decay',
      type=float,
      default=1e-4,
      help='Weight decay for convolutions.')
  parser.add_argument(
      '--learning-rate',
      type=float,
      default=0.1,
      help="""\
      This is the inital learning rate value. The learning rate will decrease
      during training. For more details check the model_fn implementation in
      this file.\
      """)
  parser.add_argument(
      '--use-distortion-for-training',
      type=bool,
      default=True,
      help='If doing image distortion for training.')
  parser.add_argument(
      '--sync',
      action='store_true',
      default=False,
      help="""\
      If present when running in a distributed environment will run on sync mode.\
      """)
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
      '--data-format',
      type=str,
      default=None,
      help="""\
      If not set, the data format best for the training device is used. 
      Allowed values: channels_first (NCHW) channels_last (NHWC).\
      """)
  parser.add_argument(
      '--log-device-placement',
      action='store_true',
      default=False,
      help='Whether to log device placement.')
  parser.add_argument(
      '--batch-norm-decay',
      type=float,
      default=0.997,
      help='Decay for batch norm.')
  parser.add_argument(
      '--batch-norm-epsilon',
      type=float,
      default=1e-5,
      help='Epsilon for batch norm.')
  parser.add_argument(
      '--work_dir',
      type=str,
      default='/data/',
      help='UAI SDK related.')
  parser.add_argument(
      '--log_dir',
      type=str,
      default='/data/data/',
      help='UAI SDK related.'
  )
  args = parser.parse_args()

  if args.num_gpus < 0:
    raise ValueError(
        'Invalid GPU count: \"--num-gpus\" must be 0 or a positive integer.')
  if args.num_gpus == 0 and args.variable_strategy == 'GPU':
    raise ValueError('num-gpus=0, CPU must be used as parameter server. Set'
                     '--variable-strategy=CPU.')
  if (args.num_layers - 2) % 6 != 0:
    raise ValueError('Invalid --num-layers parameter.')
  if args.num_gpus != 0 and args.train_batch_size % args.num_gpus != 0:
    raise ValueError('--train-batch-size must be multiple of --num-gpus.')
  if args.num_gpus != 0 and args.eval_batch_size % args.num_gpus != 0:
    raise ValueError('--eval-batch-size must be multiple of --num-gpus.')

  main(**vars(args))