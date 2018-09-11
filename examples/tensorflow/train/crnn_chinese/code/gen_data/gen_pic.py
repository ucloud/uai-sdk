# -*- coding: utf-8 -*-
from __future__ import division
"""
Created on Fri Jul 20 15:55:52 2018

@author: hou
"""
import numpy as np
import os
import cv2
import math
import skimage
import random
import argparse
from skimage import io
from PIL import Image,ImageDraw,ImageFont

parser = argparse.ArgumentParser()
parser.add_argument('--path_poem_txt', type=str,default='/data/data/gen_data/THUOCL_poem.txt',help='path of chinese char txt')
parser.add_argument('--font_path', type=str,default='/data/data/gen_data/MSYHL.TTC', help='path of font')
parser.add_argument('--pic_save_path', type=str,default='/data/data/pic', help='chinese char pic path')
parser.add_argument('--size', type=int, default=30,help='chinese char pic path')


args = parser.parse_args()

#generate chinese dict 
with open(args.path_poem_txt, 'r') as file_to_read:
    f = file_to_read.readlines()
    f = list(map(lambda line:line.split('\t')[0].strip(),f))
dict_char=dict(zip(np.arange(len(f)),f))

#generate chinese char pic
def generate(size,char,char_index,save_path,font_path,times):
    #kernel = np.ones((3,3),np.uint8) #kernel of erode or dilate 
    char=str(char)
    l_char=len(char)
    
    #char=unicode(char,'utf-8')
    #l_char=len(char)
    width=l_char*size
    img = Image.new('RGB',(width,size+20),'white')
    draw = ImageDraw.Draw(img)
    #char=unicode(char,'utf-8')
    #maxsize=min(width/l_char/height,0.8)
    #minsize=maxsize-0.1
    
    #sizeofchar=np.arange(minsize,maxsize+0.05,0.05)
    #print(round(width/l_char/height,2),maxsize,minsize)
    #sizeofchar=[0.4,0.45]
    #size= sizeofchar[random.randint(0,len(sizeofchar)-1)]
    
    font = ImageFont.truetype(font_path,size)
    draw.text((0,0),char,(0,0,0),font=font)   
    IMG_SAVEPATH = os.path.join(save_path,str(char_index))
    if (not os.path.exists(IMG_SAVEPATH)):
        os.makedirs(IMG_SAVEPATH)        
    rotate = random.randint(-2, 2)
    img = img.rotate(rotate)
    img_0 = np.array(img)
    noise_modes=['gaussian','poisson','salt','pepper']
    noise_mode=noise_modes[random.randint(0,len(noise_modes)-1)]
    img_1 = skimage.util.random_noise(img_0, mode=noise_mode,seed=None, clip=True)
    #img_2 = cv2.erode(img_0,kernel,iterations = 1)  
    #img_3 = cv2.dilate(img_0,kernel,iterations = 1) 
    #img_3 = skimage.util.random_noise(img_2, mode=noise_mode,seed=None, clip=True)
    #img_5 = skimage.util.random_noise(img_3, mode=noise_mode,seed=None, clip=True)
    for index in range(2):
        io.imsave(os.path.join(IMG_SAVEPATH,str(times)+'_'+str(index)+'.jpg'),eval('img_'+str(index)))
    
for key in dict_char: 
    for times in range(15):
        generate(args.size,dict_char[key],key,args.pic_save_path,args.font_path,times) 
        
        
