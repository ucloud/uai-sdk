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

from __future__ import print_function

import os
import sys
import cv2

from PIL import Image

class UaiOpenCVRtspProcessor:

    def __init__(self, video_stream, width, height):
        vcap = cv2.VideoCapture(video_stream)
        vcap.set(3, width)
        vcap.set(4, height)
        self._vcap = vcap

    def get_frame(self):
        """ Get Next frame of current stream

            Return: PIL.Image object
        """
        ret, frame = self._vcap.read()
        if ret is False:
            return None

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        im_pil = Image.fromarray(img)

        return im_pil

    def get_next_n_frame(self, n):
        last_frame = None
        ret = True

        i = 0
        while(i < n):
            ret, frame = self._vcap.read()
            if ret is False:
                continue

            i = i + 1
            last_frame = frame

        if last_frame is None:
            return None

        img = cv2.cvtColor(last_frame, cv2.COLOR_BGR2RGB)
        im_pil = Image.fromarray(img)
        return im_pil

    def cleanup():
        self._vcap.release()