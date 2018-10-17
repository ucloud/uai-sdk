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

"""A east text detector inferencer.

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
from PIL import Image
import tensorflow as tf
import numpy as np
import sys
import os
import copy
import argparse
import cv2
import lanms
import model
from icdar import restore_rectangle

import east_multi_infer
from uai.arch.tf_model import TFAiUcloudModel

class EASTTextDetectModel(TFAiUcloudModel):
    """ EASTTextDetectModel example model
    """

    def __init__(self, conf):
        super(EASTTextDetectModel, self).__init__(conf)

    def load_model(self):
        predictor = east_multi_infer.EastPredictor('./checkpoint_dir')
        predictor.load_serve_model()
        self._predictor = predictor

    def execute(self, data, batch_size):
        predictor = self._predictor
        ret = []

        images = []
        for i in range(batch_size):
            image = Image.open(data[i])
            images.append(image)

        results = predictor.do_serve_predict(images)

        return results

