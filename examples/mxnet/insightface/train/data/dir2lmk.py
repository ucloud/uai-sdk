# -*- coding: utf-8 -*-
from __future__ import print_function

import sys
import os
import argparse
import shutil
import cv2

import mxnet as mx
path = os.path.join(os.path.dirname(__file__), '..', '..', 'deploy')
print(path)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'deploy'))
from mtcnn_detector import MtcnnDetector
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
import face_preprocess

from PIL import Image

def preprocess_face(face_img_path, bbox, landmark):
    img = cv2.imread(face_img_path, cv2.IMREAD_COLOR)
    img = face_preprocess.preprocess(img, bbox = bbox, landmark=landmark, image_size='%d,%d'%(112, 112))
    return img

def crop_face(face_img_path, bbox, aligned_face_path):
    with Image.open(face_img_path) as img:
        img = img.crop(bbox)
        img.save(aligned_face_path)

def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Create Image Lamdmark from Dir')
    parser.add_argument('--origin_dir', type=str, help='Dir containing original images')
    parser.add_argument('--data_dir', type=str, help='Dir containing the cropped images')
    parser.add_argument('--lmk_file', type=str, default='lmk.txt', help='Target file of Lamdmark')
    parser.add_argument('--dir_prefix', type=str, default='u.', help='prefix append to each face_id')
    parser.add_argument('--start_id', type=int, default=0, help='Start Face ID, default from 0')
    parser.add_argument('--mtcnn_path', type=str, help='MTCNN model model_folder path')

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()

    if os.path.isdir(args.dir):
        img_dir = args.dir
    else:
        print('Error dir %s' % (args.dir))

    ctx = mx.gpu()
    mtcnn_path = args.mtcnn_path
    det_threshold = [0.6,0.7,0.8]
    detector = MtcnnDetector(model_folder=mtcnn_path, ctx=ctx, num_worker=1, accurate_landmark=True, threshold=det_threshold)

    start_id = args.start_id
    face_id = start_id
    aligned_data_dir = args.data_dir
    aligned_prefix = args.dir_prefix
    face_cnt = 0
    with open(args.lmk_file, 'w') as lmk_f:
        person_dirs = os.listdir(img_dir)

        # handle person by person
        if os.path.exists(aligned_data_dir) is False:
            os.mkdir(aligned_data_dir)
        for person in person_dirs:
            aligned_face_subdir = ('%s%d'%(aligned_prefix, face_id))
            aligned_persion_dir = os.path.join(aligned_data_dir, aligned_face_subdir)
            if os.path.exists(aligned_persion_dir) is False:
                os.mkdir(aligned_persion_dir)

            face_img_dir = os.path.join(img_dir, person)
            face_imgs = os.listdir(face_img_dir)
            person_cnt = 0
            lmk_infos = []
            for face in face_imgs:
                face_img_path = os.path.join(face_img_dir, face)
                det_type=0
                img = cv2.imread(face_img_path, cv2.IMREAD_COLOR)
                ret = detector.detect_face(img, det_type=det_type)
                if ret is None:
                    continue

                bbox, _ = ret
                if bbox.shape[0]==0:
                    continue

                bbox = bbox[0,0:4]
                print(bbox)
                aligned_face_filename = ('%s%s'%(face, '_align.jpg'))
                aligned_face_path = os.path.join(aligned_persion_dir, aligned_face_filename)

                _, points = ret
                points = points[0,:].reshape((2,5)).T

                img = preprocess_face(face_img_path, bbox, points)
                cv2.imwrite(aligned_face_path, img)

                lmk_info = ('%s %d %f %f %f %f %f %f %f %f %f %f\n' % (aligned_face_path, face_id,
                    points[0][0], points[0][1], points[1][0], points[1][1],
                    points[2][0], points[2][1], points[3][0], points[3][1],
                    points[4][0], points[4][1]))
                lmk_infos.append(lmk_info)
                #print(lmk_info)

                person_cnt += 1
                face_cnt += 1

            if person_cnt < 2:
                print('Fail to get more than 2 pics for %s' % (face))
                shutil.rmtree(aligned_persion_dir)
            else:
                for lmk_info in lmk_infos:
                    lmk_f.write(lmk_info)
                print('[%d][%d]Face %s under %s'%(face_cnt, person_cnt, face, aligned_persion_dir))
                face_id += 1


