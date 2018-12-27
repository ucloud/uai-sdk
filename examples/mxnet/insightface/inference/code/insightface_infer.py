# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import numpy as np
from PIL import Image
import cv2
import sklearn
from sklearn.decomposition import PCA
import sys
import mxnet as mx

from uai.arch.mxnet_model import MXNetAiUcloudModel

from mtcnn_detector import MtcnnDetector
sys.path.append(os.path.join(os.path.dirname(__file__), 'common'))
import face_image
import face_preprocess

IMAGE_SIZE = 112

def get_model(ctx, image_size, prefix, epoch, layer):
  print('loading',prefix, epoch)
  sym, arg_params, aux_params = mx.model.load_checkpoint(prefix, epoch)
  all_layers = sym.get_internals()
  sym = all_layers[layer+'_output']
  model = mx.mod.Module(symbol=sym, context=ctx, label_names=None)
  #model.bind(data_shapes=[('data', (args.batch_size, 3, image_size[0], image_size[1]))], label_shapes=[('softmax_label', (args.batch_size,))])
  model.bind(data_shapes=[('data', (1, 3, image_size[0], image_size[1]))])
  model.set_params(arg_params, aux_params)
  return model

class FaceModel:
  def __init__(self, ctx, model_prefix, model_epoch, mtcnn_det=1):
    image_size = (IMAGE_SIZE, IMAGE_SIZE)
    self.image_size = image_size
    self.model = get_model(ctx, image_size, model_prefix, model_epoch, 'fc1')

    self.det_type = mtcnn_det
    #self.det_factor = 0.9
    mtcnn_path = os.path.join(os.path.dirname(__file__), 'mtcnn-model')
    if self.det_type == 0:
      self.det_threshold = [0.6,0.7,0.8]
      detector = MtcnnDetector(model_folder=mtcnn_path, ctx=ctx, num_worker=1, accurate_landmark=True, threshold=self.det_threshold)
    else:
      self.det_threshold = [0.0,0.0,0.2]
      detector = MtcnnDetector(model_folder=mtcnn_path, ctx=ctx, num_worker=1, accurate_landmark=True, threshold=self.det_threshold)
    self.detector = detector

  def get_input(self, face_img):
    ret = self.detector.detect_face(face_img, det_type = self.det_type)
    if ret is None:
      return None
    bbox, points = ret
    if bbox.shape[0]==0:
      return None
    bbox = bbox[0,0:4]
    points = points[0,:].reshape((2,5)).T
    #print(bbox)
    #print(points)
    nimg = face_preprocess.preprocess(face_img, bbox, points, image_size='112,112')
    nimg = cv2.cvtColor(nimg, cv2.COLOR_BGR2RGB)
    aligned = np.transpose(nimg, (2,0,1))
    return aligned

  def get_feature(self, aligned):
    input_blob = np.expand_dims(aligned, axis=0)
    data = mx.nd.array(input_blob)
    db = mx.io.DataBatch(data=(data,))
    self.model.forward(db, is_train=False)
    embedding = self.model.get_outputs()[0].asnumpy()
    embedding = sklearn.preprocessing.normalize(embedding).flatten()
    return embedding

class InsightFaceModel(MXNetAiUcloudModel):
    """ Mnist example model
    """
    def __init__(self, conf):
        super(InsightFaceModel, self).__init__(conf)

    def load_model(self):
        ctx = mx.cpu()
        # ctx = mx.gpu()
        model = FaceModel(ctx, self.model_prefix, self.num_epoch)
        self._model = model

    def execute(self, data, batch_size):
        model = self._model

        ret = []
        for i in range(batch_size):
            im_data = data[i].body
            np_arr = np.fromstring(im_data, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            img = model.get_input(img)
            if img is None:
                ret.append('None')
                continue

            embedding = model.get_feature(img)
            embedding = embedding.tolist()
            ret.append(' '.join(str(x) for x in embedding))

        return ret
