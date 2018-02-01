# uai-sdk
## What is UCloud AI SDK

1. This SDK include **pack tool** to pack local AI inference program into UCloud web service image which could run on UCloud **UAI Inference** Platform.
2. This SDK include whole **APIs** which could interactive with UCloud **UAI Inference** Platform.
3. This SDK include **pack tool** to help pack local AI trainning program into UCloud Docker image which could run on UCloud **UAI Train** Platform.
4. This SDK include whole **APIs** which could interactive with UCloud **UAI Train** Platforms



## Supported AI Platform

### UAI Inference
- Tensorflow (0.11.0 tested)
- Tensorflow（1.1.0 tested）
- Tensorflow（1.2.0 tested）
- MXNet(0.9.5 tested)
- Keras(1.2.0 tested)
- Caffe(1.0.0 tested)
- Intel-Caffe

### UAI Train
- Tensorflow (0.11.0 tested)
- Tensorflow（1.1.0 tested）
- Tensorflow（1.2.0 tested）
- Tensorflow（1.3.0 tested)
- Tensorflow（1.4.0 tested）
- MXNet(0.9.5 tested)
- MXNet(1.0.0 tested)
- Keras(1.2.0 tested)
- Caffe(1.0.0 tested)
- PyTorch(0.2.0)

## How to install
1. Install your deep learning python package, such as Tensorflow, MXNet, Keras, Caffe (tested version preferred)
2. Install UCloud Ufile SDK (https://docs.ucloud.cn/storage_cdn/ufile/tools)

        $ wget http://sdk.ufile.ucloud.com.cn/python_sdk.tar.gz
        $ tar zxvf python_sdk.tar.gz
        $ cd ufile-python
        $ sudo python setup.py install

3. Install uai-sdk

        $ sudo python setup.py install

4. Install Flask

        $ sudo pip install Flask

5. Install all other lib your inference code required


## How to interactive with UCloud UAI Platform
### UAI Inference Docs
https://docs.ucloud.cn/ai/uai-service/use
### UAI Train Docs
https://docs.ucloud.cn/ai/uai-train/use
