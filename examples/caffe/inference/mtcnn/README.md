# Face Detection Alignment Example with MTCNN
This example shows how to use MTCNN to do face detection. Here we shows how to build a face detection inference service based on UAI Inference system. We assume you have already known how to get a MTCNN model (https://github.com/DuinoDu/mtcnn). 

## Intro
UAI Inference platform can serve inference services through HTTP requests. We provide the basic docker image containing a django server which can load the user-defined inference module to do the service. To implement a inference module, you only need to implement two funcs: load\_model and execute. For more details please refer to https://docs.ucloud.cn/ai/uai-inference/guide/principle.

In this example, we provide the inference service example: MTCNNCpuModel which accept one image and gives all possibile 'face' bounding boxes.

## Setup
You should download the current directory into your work place. You should also get a MTCNN caffe model (You can download it from https://github.com/DuinoDu/mtcnn), and put it under the code dir.

We put all these files into one directory:

	/data/mtcnn/inference/
	|_ code
	|  |_ model
	|  |  |_ det1.caffemodel
	|  |  |_ det1.prototxt
	|  |  |_ det2.caffemodel
	|  |  |_ det2.prototxt
	|  |  |_ det3.caffemodel
	|  |  |_ det3.prototxt
	|  |_ mtcnn_inference.py
	|  |_ mtcnn.py
	|_ mtcnn-caffe-cpu.Dockerfile
	|_ mtcnn-intel-caffe-cpu.Dockerfile
	|_ mtcnn.conf

## UAI Inference Example
We provide mtcnn\_inference.py which implements MTCNNCpuModel. For MTCNNCpuModel, it implements two funcs:

1. load\_model(self), which loads the MTCNN model. 

2. execute(self, data, batch_size), which handles the inference requests. The django server will invoke FaceCompareModel->execute when it receive requests. It will process the input 'data' array one by one which load the image from data[x] and invokes detect\_face to generate the result 'face' list. We format each result into json obj.

### Define the Config File
We need to provide the config file to tell the UAI Inference system to get the basic information to load the MTCNNCpuModel. The config file should include following info:

1. "exec" tells which file is used as the entry-point of the user-defined inference logic and which main class is used. 

You can find the example config file: mtcnn.conf

### Packing Inference Docker
We provide mtcnn-caffe-cpu.Dockerfile and mtcnn-intel-caffe-cpu.Dockerfile  for you to build the local inference docker image. Take mtcnn-caffe-cpu.Dockerfile as an example:

	FROM uhub.service.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-14.04_python-2.7.6_caffe-1.0.0:v1.2

	COPY code/ /ai-ucloud-client-django/
	COPY ./mtcnn.conf /ai-ucloud-client-django/ufile.json
	EXPOSE 8080
	ENV UAI_SERVICE_CONFIG "ufile.json"
	CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi

1. build the docker image based on UCloud AI Inference Docker base image. (Note if you are using UCloud VM you can use 'uhub.service.ucloud.cn' otherwise you should change it into 'uhub.ucloud.cn'
2. EXPOSE 8080 port for http service
3. ADD all code under ./code into /ai-ucloud-client-django/. (Note the root path when the django server start is /ai-ucloud-client-django/)
4. ADD the conf.json into /ai-ucloud-client-django/, The django server will automatically load a json config file to get all running info. For more details of how json file is organized please refer: [Define the Config File](#define-the-config-file)
5. Set the UAI_SERVICE_CONFIG environment to tell django server to load the config file named 'conf.json'
6. use gunicorn to run the server

### Build Your Own Inference Docker
With the above docker file we can now build your own inference docker image(Your directory should looks like [Setup](#setup)):

    sudo docker build -t mtcnn:test -f mtcnn-caffe-cpu.Dockerfile .

    sudo docker build -t mtcnn-intel:test -f mtcnn-intel-caffe-cpu.Dockerfile .


### Run MTCNN Inference Service Locally
We can run the mtcnn server as

    sudo docker run -it -p 8080:8080 mtcnn:test

You can run the face-embed server as 

    sudo docker run -it -p 8080:8080 mtcnn-intel:test


### Test MTCNN Inference Service Locally
MTCNNCpuModel takes image obj as input (png or jpeg)

	$ curl -X POST http://127.0.0.1:8080/service -T 1.png

**Note: We set http request timeout to 10 seconds in the gunicorn. You can change it by modify /ai-ucloud-client-django/gunicorn.conf.py (inside docker img) to change the timeout setting.**

## Deploy MTCNN Inference Service into UAI Inference Platform
Please refer to https://docs.ucloud.cn/ai/uai-inference/index for more details. You can directly use the docker image build in [Build](#build-your-own-inference-docker)