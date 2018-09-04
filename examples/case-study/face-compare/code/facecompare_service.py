# Copyright 2017 The UAI-SDK Authors. All Rights Reserved. 
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

"""An example face compare example

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import numpy as np
import sys
import os
import copy
import argparse
import json
import requests

from uai.arch.base_model import AiUcloudModel
from uai.arch_conf.base_conf import ArchJsonConfLoader

from uai.contrib.image import img_utils

class FaceCompareService(AiUcloudModel):

    def __init__(self, conf):
        super(FaceCompareService, self).__init__(conf, "None")
        self.load_model()

    def _parse_conf(self, conf):
        pass

    def load_model(self):
        mtcnn_backend = self.conf['backend']['mtcnn']
        facecompare_backend = self.conf['backend']['compare']

        self._mtcnn_backend = mtcnn_backend
        self._facecompare_backend  = facecompare_backend
        print(self._mtcnn_backend)
        print(self._facecompare_backend)

    def mtcnn_face(self, image):
        img_encode = img_utils.encode_images_to_json([image])
        response = requests.post(self._mtcnn_backend, data=img_encode, timeout=20)
        
        if response.ok is False:
            return None

        try:
            points = json.loads(response.text)
            points = points['bounds'][0]
        except:
            return None
        
        print(points[0:4])
        image = image.crop(points[0:4])
        return image

    def compare_face(self, data):
        _, image_list = img_utils.decode_json_to_images(data)
        if len(image_list) != 2:
            return -1

        face0 = self.mtcnn_face(image_list[0])
        face1 = self.mtcnn_face(image_list[1]) 

        if face0 is None or face1 is None:
            return -1
        face_data = img_utils.encode_images_to_json([face0, face1])
        score = requests.post(self._facecompare_backend, data=face_data, timeout=60)

        return score

    def execute(self, data, batch_size):
        ret = []
        for i in range(batch_size):
            ret_val = self.compare_face(data[i].body)

            ret.append(ret_val)

        return ret