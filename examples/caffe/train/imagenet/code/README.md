# Resnet101 for imagenet lmdb
Then resnet prototxt is from https://github.com/yihui-he/resnet-imagenet-caffe

## Data Prepare
To generate lmdb data please See https://github.com/BVLC/caffe/tree/master/examples/imagenet, You can use examples/imagenet/create_imagenet.sh to generate imagenet lmdb files

This will generate:
'''bash
ilsvrc12_train_lmdb/data.mdb
ilsvrc12_train_lmdb/lock.mdb
ilsvrc12_val_lmdb/data.mdb
ilsvrc12_val_lmdb/lock.mdb
'''

### Work with ufile
To run training with UAI Train Platform with ufile as data backend, we should split both train data.mdb and val data.mdb into chunchs with uaitrain_tools/split_tool.py

Also we should use uaitrain/arch/caffe/train_large_file.py as the train entrance
