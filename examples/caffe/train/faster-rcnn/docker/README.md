# py-faster-rcnn Docker Image Example
This example shows how to build a caffe docker image. We take py-faster-rcnn(https://github.com/rbgirshick/py-faster-rcnn) as an example. It includes building the py-caffe from caffe source and build the fast\_rcnn modules (bbox, nms).

## Preparation
You should download the fast-rcnn code and uai-sdk:

	# cd /data/fast-rcnn/
	# mkdir docker_file
	# cd docker_file
	# git clone https://github.com/rbgirshick/py-faster-rcnn.git --recursive
	# git clone https://github.com/ucloud/uai-sdk.git

	# cp <PATH_TO_FASTER_RCNN_BUILD_EXAMPLE>/gpu_ubuntu-14.04_python-2.7.6_caffe-py-faster-rcnn.Dockerfile ./

Now we get:

	```
	/data/fast-rcnn/
	|_ docker_file
	|  |_ py-faster-rcnn
	|  |  |_ caffe-fast-rcnn
	|  |  |  |_ ...
	|  |  |  |_ ...
	|  |  |_ data
	|  |  |_ experiments
	|  |  |_ lib
	|  |  |_ Makefile.config 
	|  |  |_ models
	|  |  |_ tools
	|  |_ uai-sdk
	|  |  |_ ...
	|_ gpu_ubuntu-14.04_python-2.7.6_caffe-py-faster-rcnn.Dockerfile
	|_ Makefile.config
	```

### Config Caffe Makefile.config
We provide the Makefile.config which is compatable with ubuntu base image and cuda8+cudnn6. You can modify the Makefile.config yourself. You can change the original Makefile.config by:

	cp Makefile.config docker_file/py-faster-rcnn/caffe-fast-rcnn/

### Preparing the Dockerfile
We provide the gpu\_ubuntu-14.04\_python-2.7.6\_caffe-py-faster-rcnn.Dockerfile to you. It contains four parts:

A. Install base packages, it will install basic apt-packages and pip-packages: 

	FROM uhub.service.ucloud.cn/uaishare/nvidia-cudnn6.0.21-cuda8.0:v1.0

	RUN apt-get update
	RUN apt-get install -y libprotobuf-dev \
	                       libleveldb-dev \
	                       libsnappy-dev \
	                       libopencv-dev \
	                       libhdf5-serial-dev \
	                       protobuf-compiler \
	                       libgflags-dev \
	                       libgoogle-glog-dev \
	                       liblmdb-dev \
	                       libopenblas-dev

	RUN apt-get update

	RUN apt-get install -y --no-install-recommends libboost-all-dev libatlas-base-dev libhdf5-dev python-tk \
	        && \
	    apt-get clean && \
	    rm -rf /var/lib/apt/lists/*

	RUN pip install numpy cython opencv-python easydict -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com

B. Build Caffe. It will copy the py-faster-rcnn into Docker Container, build the pycaffe module first, and build the py-faster-rcnn/lib.

	ADD ./docker_file/py-faster-rcnn/ /root/py-faster-rcnn

	RUN cd /root/py-faster-rcnn/caffe-fast-rcnn/python && for req in $(cat requirements.txt); do pip install $req -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com; done

	RUN cd /root/py-faster-rcnn/caffe-fast-rcnn/ && make all -j8 && make pycaffe
	RUN cd /root/py-faster-rcnn/lib && make

C. Install docker_file/uai-sdk
	
	ADD ./uai-sdk /uai-sdk
	RUN cd /uai-sdk && /usr/bin/python setup.py install

D. Setup python path

	RUN ln -s /dev/null dev/raw1394
	ENV PYTHONPATH=/root/py-faster-rcnn/caffe-fast-rcnn/python

### Updating cudnn files
As py-faster-rcnn/caffe-fast-rcnn is not fresh enough to use cuda8+cudnn6. You should switch several files with newest files from BVLC caffe

1. switch py-faster-rcnn/caffe-fast-rcnn/include/caffe/util/cudnn.hpp
2. switch all files start with cudnn\_* under py-faster-rcnn/caffe-fast-rcnn/include/caffe/layers/
3. switch py-faster-rcnn/caffe-fast-rcnn/src/caffe/util/cudnn.cpp
4. switch all files start with cudnn\_* under py-faster-rcnn/caffe-fast-rcnn/src/caffe/layers/

## Build the docker image
After preparing all files like [Preparation](#Preparation), you can use gpu\_ubuntu-14.04\_python-2.7.6\_caffe-py-faster-rcnn.Dockerfile to build the docker image directly.

	sudo docker build -t py-faster-rcnn-base:v1.0 -f gpu_ubuntu-14.04_python-2.7.6_caffe-py-faster-rcnn.Dockerfile .
