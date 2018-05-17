# EAST Inference Example
This example shows how to use EAST to do text detection inference. Here we show how to build a text detection inference service based on UAI Inference system. We assume you have already known how to train an EAST model (https://github.com/argman/EAST or https://github.com/ucloud/uai-sdk/tree/master/examples/tensorflow/train/east).

## Intro
UAI Inference platform can serve inference services through HTTP requests. We provide the basic docker image containing a django server which can load the user-defined inference module to do the service. To implement a inference module, you only need to implement two funcs: load\_model and execute. For more details please refer to https://docs.ucloud.cn/ai/uai-inference/guide/principle.

In this example, we provide the inference example of text detection using EAST: EASTTextDetectModel. It accept a 'text' image and return a list of detected boxes.

## Setup
You should download the current directory into your work place. You should also train a EAST model (https://github.com/argman/EAST or https://github.com/ucloud/uai-sdk/tree/master/examples/tensorflow/train/east) or download one from https://github.com/argman/EAST, and put it under the code/checkpoint\_dir/ dir.

We put all these files into one directory:

	/data/east/inference/
	|_ code
	|  |_ lanms
	|  |_ nets
	|  |_ data_util.py
	|  |_ east_inference.py
	|  |_ icdar.py
	|  |_ model.py
	|  |_ checkpoint_dir
	|  |  |_ checkpoint
	|  |  |_ model.ckpt-xxx
	|  |  |_ model.ckpt-xxx.index
	|  |  |_ model.ckpt-xxx.meta
	|_ east.conf
	|_ east.Dockerfile

## UAI Inference Example
We provide east\_inference.py which implements EASTTextDetectModel. For EASTTextDetectModel, it implements two funcs:

1. load\_model(self), which loads the EAST model from checkpoint\_dir. It first load the graph defination an then restore the model.

2. execute(self, data, batch_size), which handles the inference requests. The django server will invoke EASTTextDetectModel->execute when it receives requests. It will buffer requests into a array named 'data' when possible. In execute(), it first preprocesses the input 'data' array by invoking self.resize_image() for each data[i] and merge all preprocessed images into one batch, then calculates the image score and geometry. After getting the score and geometry, it will 'detecting' the text boxes for each request one by one. It formats resulting boxes into list object. (You can format it into json also)

### Define the Config File
We need to provide the config file to tell the UAI Inference system to get the basic information to load the EASTTextDetectModel and the EAST model. The config file should include following info:

1. "exec" tells which file is used as the entry-point of the user-defined inference logic and which main class is used. 
2. "tensorflow" tells which model related info should be parsed by UAI Inference system.

You can find the example config file of: east.conf

### Packing Inference Docker
We provide east-cpu.Dockerfile for you to build the local inference docker image. 

	FROM uhub.service.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-16.04_python-2.7.6_tensorflow-1.6.0:v1.0

	RUN apt-get update && apt-get install -y --no-install-recommends  python-dev python-tk

	RUN pip install shapely -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com

	EXPOSE 8080
	ADD ./code/ /ai-ucloud-client-django/
	RUN cd /ai-ucloud-client-django/lanms/&&make
	ADD ./east.conf  /ai-ucloud-client-django/conf.json
	ENV UAI_SERVICE_CONFIG /ai-ucloud-client-django/conf.json
	CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi

1. build the docker image based on UCloud AI Inference Docker base image. (Note if you are using UCloud VM you can use 'uhub.service.ucloud.cn' otherwise you should change it into 'uhub.ucloud.cn'
2. install python-dev and python-tk, python-dev is necessary for build lanms module
3. install shapely pip package
4. EXPOSE 8080 port for http service
5. ADD all code under ./code into /ai-ucloud-client-django/. (Note the root path when the django server start is /ai-ucloud-client-django/)
6. go to /ai-ucloud-client-django/lanms/ to build lanms module
7. ADD the conf.json into /ai-ucloud-client-django/, The django server will automatically load a json config file to get all running info. For more details of how json file is organized please refer: [Define the Config File](#define-the-config-file)
8. Set the UAI_SERVICE_CONFIG environment to tell django server to load the config file named 'conf.json'
9. use gunicorn to run the server

### Build Your Own Inference Docker
With the above docker file we can now build your own inference docker image(Your directory should looks like [Setup](#setup)):

	sudo docker build -t east-inference:test -f east-cpu.Dockerfile .

### Run EAST Inference Service Locally
You can run the east-inference server as:

	sudo docker run -it -p 8080:8080 east-inference:test

### Test EAST Inference Service Locally
You can test the east-inference server as:

	curl -X POST http://localhost:8080/service -T xxx.jpeg

## Deploy EAST Inference Service into UAI Inference Platform
Please refer to https://docs.ucloud.cn/ai/uai-inference/index for more details. You can directly use the docker image build in [Build](#build-your-own-inference-docker)
