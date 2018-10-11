""" input a list of files and pack them into json file """

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from scipy import misc

import sys
import os
import argparse
import json
import base64
import StringIO

def main(args):
    images = load_images(args.image_files, args.image_size)
    cnt = len(images)
    raw_images = []
    for image in images:
        buf = StringIO.StringIO()
        image.save(buf, format='PNG')
        image = base64.b64encode(buf.getvalue())
        raw_images.append(image)

    json_data = {'cnt': cnt, 'images': raw_images}

    with open('test.json', 'w') as f:
        json.dump(json_data, f)

def load_images(tmp_image_paths, image_size):
    img_list = []
    for image in tmp_image_paths:
        img = misc.imread(os.path.expanduser(image), mode='RGB')
        img = misc.imresize(img,(image_size, image_size), interp='bilinear')
        im = misc.toimage(img)
        img_list.append(im)

    return img_list

def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--image_files', type=str, nargs='+', help='Images to compare')
    parser.add_argument('--image_size', type=int,
            help='Image size (height, width) in pixels.', default=160)
    return parser.parse_args(argv)

if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))