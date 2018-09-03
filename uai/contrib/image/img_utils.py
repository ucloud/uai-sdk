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

""" Perform image encode/decode
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from PIL import Image

import json
import base64
import StringIO

def encode_images_to_json(image_list, key='imgs'):
    """
    input:
        key: key for the json object
        image_list: a list of Image object

    return:
        a json string contain images with base64 encoded
    """
    raw_images = []
    for image in image_list:
        buf = StringIO.StringIO()
        image.convert('RGB').save(buf, format="JPEG")
        image = base64.b64encode(buf.getvalue())
        raw_images.append(image)

    json_data = {key: raw_images}
    return json.dumps(json_data)

def decode_json_to_images(json_data):
    """
    input:
        json object produced by encode_images_to_json
    return:
        key name
        list of PIL.Image
    """
    data = json.loads(json_data)
    key = data.keys()[0]
    value = data.values()[0]

    image_list = []
    for raw_image in value:
        img_data = raw_image.decode('base64')
        img = Image.open(StringIO.StringIO(img_data))
        image_list.append(img)

    return key, image_list

if __name__ == "__main__":
    img1 = Image.open('0.png')
    img2 = Image.open('1.png')

    key = 'image'
    image_list = [img1, img2]

    data = encode_images_to_json(key, image_list)
    key_r, img_l = decode_json_to_images(data)
