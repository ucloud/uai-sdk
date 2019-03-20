import json
import os
import tensorflow as tf
import numpy as np
from absl import app
from absl import flags
import sys

import mnist_data
from tensorflow.python.keras.utils import *

import logging
logging.getLogger().setLevel(logging.INFO)

FLAGS = app.flags.FLAGS
flags = app.flags

# =======================================================================
# Constant variables
# --work_dir=/data
# --data_dir=/data/data
# --output_dir=/data/output
#
# Note: Use this params as contant values
#       Do not set this params !!!       
# =======================================================================
flags.DEFINE_string("work_dir", "/data", "Default work path")
flags.DEFINE_string("data_dir", "/data/data", "Default data path")
flags.DEFINE_string("output_dir", "/data/output", "Default output path")
flags.DEFINE_integer("num_gpus", 0, "Num of avaliable gpus")

# How many categories we are predicting from (0-9)
LABEL_DIMENSIONS = 10

def get_input():
  (train_images, train_labels), (test_images, test_labels) = mnist_data.load_data()
  TRAINING_SIZE = len(train_images)
  TEST_SIZE = len(test_images)

  train_images = np.asarray(train_images, dtype=np.float32) / 255

  # Convert the train images and add channels
  train_images = train_images.reshape((TRAINING_SIZE, 28, 28, 1))

  test_images = np.asarray(test_images, dtype=np.float32) / 255
  # Convert the train images and add channels
  test_images = test_images.reshape((TEST_SIZE, 28, 28, 1))

  train_labels  = tf.keras.utils.to_categorical(train_labels, LABEL_DIMENSIONS)
  test_labels = tf.keras.utils.to_categorical(test_labels, LABEL_DIMENSIONS)

  # Cast the labels to floats, needed later
  train_labels = train_labels.astype(np.float32)
  test_labels = test_labels.astype(np.float32)

  return train_images, train_labels, test_images, test_labels

def build_model():
  inputs = tf.keras.Input(shape=(28,28,1))  # Returns a placeholder tensor
  x = tf.keras.layers.Conv2D(filters=32, kernel_size=(3, 3), activation=tf.nn.relu)(inputs)
  x = tf.keras.layers.MaxPooling2D(pool_size=(2, 2), strides=2)(x)
  x = tf.keras.layers.Conv2D(filters=64, kernel_size=(3, 3), activation=tf.nn.relu)(x)
  x = tf.keras.layers.MaxPooling2D(pool_size=(2, 2), strides=2)(x)
  x = tf.keras.layers.Conv2D(filters=64, kernel_size=(3, 3), activation=tf.nn.relu)(x)
  x = tf.keras.layers.Flatten()(x)
  x = tf.keras.layers.Dense(64, activation=tf.nn.relu)(x)
  predictions = tf.keras.layers.Dense(LABEL_DIMENSIONS, activation=tf.nn.softmax)(x)

  model = tf.keras.Model(inputs=inputs, outputs=predictions)
  optimizer = tf.compat.v1.train.AdamOptimizer(learning_rate=0.001)
  model.compile(loss='categorical_crossentropy',
                optimizer=optimizer,
                metrics=['accuracy'])

  return model

def input_fn(images, labels, repeat, batch_size):
  # Convert the inputs to a Dataset.
  dataset = tf.data.Dataset.from_tensor_slices((images, labels))

  # Shuffle, repeat, and batch the examples.
  SHUFFLE_SIZE = 10000
  dataset = dataset.shuffle(SHUFFLE_SIZE).repeat(repeat).batch(batch_size)

  # Return the dataset.
  return dataset

def train():
  if 'TF_CONFIG' in os.environ:
    tf_dist_conf = os.environ['TF_CONFIG']
    conf = json.loads(tf_dist_conf)
    if conf['task']['type'] == 'ps':
      is_ps = True
    else:
      is_ps = False

    if conf['task']['type'] == 'master':
      conf['task']['type'] = 'chief'
 
    conf['cluster']['chief'] = conf['cluster']['master']
    del conf['cluster']['master']
    print(conf)
    os.environ['TF_CONFIG'] = json.dumps(conf)
  else:
    return

  model = build_model()

  train_images = None
  train_labels = None
  test_images = None
  test_labels = None
 
  if is_ps:
    distribution = tf.distribute.experimental.ParameterServerStrategy()
  else:
    distribution = tf.distribute.experimental.MultiWorkerMirroredStrategy()
  config = tf.estimator.RunConfig(train_distribute=distribution)
  estimator = tf.keras.estimator.model_to_estimator(model, model_dir=FLAGS.output_dir, config=config)
  
  train_images, train_labels, test_images, test_labels = get_input()

  BATCH_SIZE=64
  EPOCHS=5
  STEPS = 1000

  train_spec = tf.estimator.TrainSpec(input_fn=lambda:input_fn(train_images,
                                         train_labels,
                                         repeat=EPOCHS,
                                         batch_size=BATCH_SIZE), 
                                         max_steps=STEPS)

  eval_spec = tf.estimator.EvalSpec(input_fn=lambda:input_fn(test_images,
                                         test_labels,
                                         repeat=1,
                                         batch_size=BATCH_SIZE),
                                         steps=100,
                                         start_delay_secs=0)
     
  tf.estimator.train_and_evaluate(
    estimator,
    train_spec,
    eval_spec)

def main(_):
  train()

if __name__ == '__main__':
  app.run(main)