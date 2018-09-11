#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-11-9 下午1:43
# @Author  : Luo Yao
# @Site    : http://github.com/TJCVRS
# @File    : establish_char_dict.py
# @IDE: PyCharm Community Edition
"""
Establish a char dict used for encode and decode label

The example dict text file is stored in data/char_dict/chinese_dict.txt
"""
import argparse
import os
import os.path as ops
import sys

sys.path.append('/data/code')

from local_utils import establish_char_dict


def init_args():
    """

    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--char_dict_file', type=str,default='/data/data/chinese.txt' ,help='The char dict file')
    parser.add_argument('--save_dir', type=str, help='The save dir path', default='/data/data/char_dict')

    return parser.parse_args()


def generate_char_dict(char_dict_file, save_dir):
    """
        Example char dict file is stored in data/char_dict/chinese_dict.txt
    :param char_dict_file:
    :param save_dir:
    :return:
    """
    generator = establish_char_dict.CharDictBuilder()

    char_dict_path = ops.join(save_dir, 'char_dict.json')
    ord_2_index_map_path = ops.join(save_dir, 'ord_2_index_map.json')
    index_2_ord_map_path = ops.join(save_dir, 'index_2_ord_map.json')

    generator.write_char_dict(char_dict_file, char_dict_path)
    generator.map_ord_to_index(char_dict_file, ord_2_index_map_path)
    generator.map_index_to_ord(char_dict_file, index_2_ord_map_path)

    print('Generate {:s}, {:s} and {:s} complete'.format(char_dict_path, ord_2_index_map_path, index_2_ord_map_path))

    return


if __name__ == '__main__':
    # init args
    args = init_args()

    assert ops.exists(args.char_dict_file)
    if not ops.exists(args.save_dir):
        os.makedirs(args.save_dir)

    # establish char dict
    generate_char_dict(args.char_dict_file, args.save_dir)
