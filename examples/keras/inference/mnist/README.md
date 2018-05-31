# MNIST Example
This example show how to run mnist inference based on UAI Inference Platform.

## Intro
UAI Inference platform can serve inference services through HTTP requests. We provide the basic docker image containing a django server which can load the user-defined inference module to do the service. To implement a inference module, you only need to implement two funcs: load\_model and execute. For more details please refer to https://docs.ucloud.cn/ai/uai-inference/guide/principle.

In this example, we provide the inference service example: MnistModel which accepts one image and gives hand writing number detection result.

## Setup
You should follow https://github.com/ucloud/uai-sdk/tree/master/examples/keras/train/mnist to train your own mnist model or you can use the one we provided in ./checkpoint_dir

We put all these files into one directory:

	/data/mnist/inference/
	|_ code
	|  |_ checkpoint_dir
	|  |  |_ checkpoint
	|  |  |_ mnist_model.h5
	|  |  |_ mnist_model.json	
	|  |_ mnist_inference.py
	|_ keras_mnist.conf
	|_ mnist-cpu.Dockerfile

## UAI Inference Example
We provide mnist\_inference.py which implements MnistModel. For MnistModel, it implements two funcs:

1. load\_model(self), which loads the MNIST model. 

2. execute(self, data, batch_size), which handles the inference requests. The django server will invoke MnistModel->execute when it receive requests. It will process the input 'data' array one by one which load the image from data[x] and invokes mnist detect to generate the result list. 

### Define the Config File
We need to provide the config file to tell the UAI Inference system to get the basic information to load the MnistModel. The config file should include following info:

1. "exec" tells which file is used as the entry-point of the user-defined inference logic and which main class is used. 
2. "keras" tells which model related info should be loaded by UAI Inference system.

You can find the example config file: keras_mnist.conf

### Packing Inference Docker
We provide mnist-cpu.Dockerfile for you to build local inference docker image.

	FROM uhub.service.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-14.04_python-2.7.6_keras-1.2.0:v1.2

	EXPOSE 8080
	ADD ./code/ /ai-ucloud-client-django/
	ADD ./keras_mnist.conf  /ai-ucloud-client-django/conf.json
	ENV UAI_SERVICE_CONFIG /ai-ucloud-client-django/conf.json
	CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi

1. build the docker image based on UCloud AI Inference Docker base image. (Note if you are using UCloud VM you can use 'uhub.service.ucloud.cn' otherwise you should change it into 'uhub.ucloud.cn'
2. EXPOSE 8080 port for http service
3. ADD all code under ./code into /ai-ucloud-client-django/. (Note the root path when the django server start is /ai-ucloud-client-django/)
4. ADD the conf.json into /ai-ucloud-client-django/, The django server will automatically load a json config file to get all running info. For more details of how json file is organized please refer: [Define the Config File](#define-the-config-file)
5. Set the UAI_SERVICE_CONFIG environment to tell django server to load the config file named 'conf.json'
6. use gunicorn to run the server

**We also provide mnist-gpu.Dockerfile to help you build the GPU docker image. It acts same as mnist-cpu.Dockerfile except using a different base image**

### Build Your Own Inference Docker
With the above docker file we can now build your own inference docker image(Your directory should looks like [Setup](#setup)):

	sudo docker build -t mnist-inference:test -f mnist-cpu.Dockerfile .

### Run Mnist Inference Service Locally
You can run the mnist-inference cpu server as:

	sudo docker run -it -p 8080:8080 mnist-inference:test

### Test Mnist Inference Service Locally
You can test the mnist-inference server as:

	curl -X POST http://localhost:8080/service -T 2.jpeg

## Deploy Mnist Inference Service into UAI Inference Platform
Please refer to https://docs.ucloud.cn/ai/uai-inference/index for more details. You can directly use the docker image build in [Build](#build-your-own-inference-docker)