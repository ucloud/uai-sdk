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

""" input a list of files and pack them into json file """

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from PIL import Image  

import sys
import os
import argparse
import json
import base64
import StringIO

from uai.contrib.image import img_utils

def main(args):
    images = load_images(args.image_files, args.image_size)
    json_data = img_utils.encode_images_to_json(images)

    with open('test.json', 'w') as f:
        f.write(json_data)

def load_images(tmp_image_paths, image_size):
    img_list = []
    for image in tmp_image_paths:
        img = Image.open(os.path.expanduser(image))
        img_list.append(img)

    return img_list

def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--image_files', type=str, nargs='+', help='Images to compare')
    parser.add_argument('--image_size', type=int,
            help='Image size (height, width) in pixels.', default=160)
    return parser.parse_args(argv)

if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
