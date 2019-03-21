# Uaitrain tools
## Basic tools
1. base_tools.py general uaitrain tool
2. tf/tf_tools.py uaitrain tool for tensorflow only
3. caffe/caffe_tools.py uaitrain tool for caffe only
4. keras/keras_tools.py uaitrain tool for keras only
5. mxnet/mxnet_tools.py uaitrain tool for mxnet only
6. pytorch/pytorch_tools.py uaitrain tool for pytorch only

For more details please see: https://docs.ucloud.cn/ai/uai-train/guide/scripts

## Helper tools
1. split_tools.py, help split a large file into small chuncks, especially for caffe lmdb files. As UAI Train platform perform to download large file from ufile, it is better to split it out at beginning to help upload the file into ufile and merge it before training (Uploading and download large file 100GB+ is fragile).

         How to split:
           python split_tools.py <file_dir> <file_name> <target_file>

         How to merge:
           See uaitrain/arch/caffe/train_large_file.py
