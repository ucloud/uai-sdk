# Copyright 2019 The UAI-SDK Authors. All Rights Reserved. 
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


import os

import tensorflow as tf
from absl import app
from absl import flags

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


def train():
  mnist = tf.keras.datasets.mnist

  (x_train, y_train),(x_test, y_test) = mnist.load_data(path=FLAGS.data_dir)
  x_train, x_test = x_train / 255.0, x_test / 255.0

  model = tf.keras.models.Sequential([
    tf.keras.layers.Flatten(input_shape=(28, 28)),
    tf.keras.layers.Dense(512, activation=tf.nn.relu),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(10, activation=tf.nn.softmax)
  ])
  model.compile(optimizer='adam',
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy'])

  model.fit(x_train, y_train, epochs=5)
  output_path = os.path.join(FLAGS.output_dir, 'mnist.h5')
  model.save(output_path)

def main(_):
  train()

if __name__ == '__main__':
  app.run(main)