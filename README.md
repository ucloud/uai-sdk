# uai-sdk
## What is UCloud AI SDK

1. This SDK include **pack tool** to pack local AI inference program into UCloud web service image which could run on UCloud **UAI Inference** Platform.
2. This SDK include whole **APIs** which could interactive with UCloud **UAI Inference** Platform.
3. This SDK include **pack tool** to help pack local AI trainning program into UCloud Docker image which could run on UCloud **UAI Train** Platform.
4. This SDK include whole **APIs** which could interactive with UCloud **UAI Train** Platforms



## Supported AI Platform

### UAI Inference

**CHECK ON**：[UAI Inference Base Docker Images](https://docs.ucloud.cn/ai/uai-inference/general/dockers)

#### 1. GPU
- Tensorflow (1.6.0 tested)
- Tensorflow (1.7.0 tested)
- Caffe (1.0.0 tested)

#### 2. CPU
- Tensorflow (1.1.0 tested）
- Tensorflow (1.2.0 tested）
- Tensorflow (1.3.0 tested)
- Tensorflow (1.4.0 tested)
- Tensorflow (1.6.0 tested)
- Tensorflow (1.7.0 tested)
- MXNet (0.9.5 tested)
- MXNet (1.0.0 tested)
- Keras (1.2.0 tested)
- Keras (2.0.8 tested)
- Caffe (1.0.0 tested)
- Intel-Caffe
- XGBoost (0.7 tested, python interface only)

### UAI Train

**CHECK ON**：[UAI Train Base Docker Images](https://docs.ucloud.cn/ai/uai-train/general/dockers)

- Tensorflow (0.11.0 tested)
- Tensorflow（1.1.0 tested）
- Tensorflow（1.2.0 tested）
- Tensorflow（1.3.0 tested)
- Tensorflow（1.4.0 tested）
- Tensorflow（1.5.0, cuda9 tested)
- Tensorflow（1.6.0, cuda9 tested）
- Tensorflow (1.7.0, cuda9 tested)
- Tensorflow (1.8.0, cuda9 tested)
- Tensorflow (1.9.0, cuda9 tested)
- MXNet (0.9.5 tested)
- MXNet (1.0.0, cuda9 tested)
- Keras (2.0.8 tested)
- Keras (2.1.6, tf-1.8 testes)
- Caffe (1.0.0 tested)
- Caffe2 (Detection)
- PyTorch (0.2.0)
- PyTorch (0.4)

### UAI Train Supporting Distributed Training
- Tensorflow Distributed Training (examples include slim/cifar/wide-deep)
- MXNet Distributed Training

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
https://docs.ucloud.cn/ai/uai-inference/index
### UAI Train Docs
https://docs.ucloud.cn/ai/uai-train/use
