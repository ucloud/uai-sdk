# -*- coding: utf-8 -*-
"""
Created on Sun Jul 22 15:38:24 2018

@author: hou
"""
import random
import argparse
import os
import numpy as np
import os.path as ops

parser = argparse.ArgumentParser()
parser.add_argument('--path_poem_txt', type=str,default='/data/data/gen_data/THUOCL_poem.txt', help='path of chinese char txt')
parser.add_argument('--pic_save_path', type=str,default='/data/data/pic' ,help='chinese char pic path')
parser.add_argument('--sample_train', type=str,default='/data/data/Train/', help='path of sample.txt used for training')
parser.add_argument('--sample_test', type=str,default='/data/data/Test/', help='path of sample.txt used for testing')
args = parser.parse_args()

with open(args.path_poem_txt, 'r') as file_to_read:
     f = file_to_read.readlines()
     f = list(map(lambda line:line.split('\t')[0].strip(),f))
dict_char=dict(zip(np.arange(len(f)),f))

#generate sample.txt  
def write_sample(save_path,sample_train,sample_test):
    img_list=os.listdir(save_path)
    num_char=len(dict_char)*30
    shuffle=np.arange(num_char)
    np.random.shuffle(shuffle)
    test_shuffle=shuffle[:int(num_char*0.3)]
    sample_toppath=sample_train
    if not ops.exists(sample_train):
       os.makedirs(sample_train)
    if not ops.exists(sample_test):
       os.makedirs(sample_test)
    
    samptrain_to_write = open(sample_train+'sample.txt', 'w')
    samptest_to_write = open(sample_test+'sample.txt', 'w')
    i=0
    #sample_toppath=sample_train.split('sample.txt')[0]
    for dirpath,dirnames,filenames in os.walk(save_path):
        relpath=os.path.relpath(dirpath,sample_toppath).split('.')[-1][1:]
        for filename in filenames:   
            i+=1
            samptrain_to_write.write(relpath+'/'+filename+' '+ dict_char[int(dirpath.split('/')[-1])]+'\n')
            if i in  test_shuffle:
                samptest_to_write.write(relpath+'/'+filename+' '+dict_char[int(dirpath.split('/')[-1])]+'\n')
    samptrain_to_write.close()
    samptest_to_write.close()

write_sample(args.pic_save_path,args.sample_train,args.sample_test)       
