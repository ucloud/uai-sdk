# -*- coding: utf-8 -*-
import io
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--path_poem_txt', type=str,default='/data/data/gen_data/THUOCL_poem.txt',help='path of chinese char txt')
parser.add_argument('--txt_save_path', type=str, help='chinese char pic path',default='/data/data/chinese.txt')

args = parser.parse_args()

def writetxt(path_poem_txt,txt_save_path):
    with open(path_poem_txt,'r') as file_to_read:
         f = file_to_read.readlines()
         f = list(map(lambda line:line.split('\t')[0].strip(),f))
         f = ''.join(f)
         f = list(set(f))      
    
    chinese=io.open(txt_save_path,'w',encoding='utf-8')
    for char in enumerate(f):
        #if char not in f[:index]:
        chinese.write(char[1]+'\n')
    chinese.close()
    file_to_read.close()

writetxt(args.path_poem_txt,args.txt_save_path)  
