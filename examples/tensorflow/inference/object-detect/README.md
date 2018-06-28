# Object Detection Example
This example show how to run object detection inference based on UAI Inference Platform.
## Origin
Creating accurate machine learning models capable of localizing and identifying multiple objects in a single image remains a core challenge in computer vision. The TensorFlow Object Detection API is an open source framework built on top of TensorFlow that makes it easy to construct, train and deploy object detection models. At Google we’ve certainly found this codebase to be useful for our computer vision needs, and we hope that you will as well. Refer to: https://github.com/tensorflow/models/tree/master/research/object_detection for the origin of this example. Some of the source code are redistributed and reproduced from this origin, with the license attached at the top of each of these code files. Also refer to the license file of this directory for the license information.


## Intro
UAI Inference platform can serve inference services through HTTP requests. We provide the basic docker image containing a django server which can load the user-defined inference module to do the service. To implement a inference module, you only need to implement two funcs: load\_model and execute. For more details please refer to https://docs.ucloud.cn/ai/uai-inference/guide/principle.

In this example, we provide the inference service example: ObjectDetectModel which accepts one image and gives object detection result.

## Setup
Get the pbtxt containing the dictionary that matches indices and categories.
Acquire an object detection model with images of the categorical objects you wish to detect. Refer to:
https://github.com/FinchZHU/uai-sdk/new/master/examples/tensorflow/inference/object-detect
for training a model of self-sourced dataset and how the pbtxt is formed. Some trained model examples are available at:
https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md

Export the model into a frozen_inference_graph.pb file if it is yet not exported.
We put all these files into one directory:

	/data/object-detect/
	|_ code
	|  |_ checkpoint_dir
	|  |  |_ frozen_inference_graph.pb
	|  |  |_ label_map.pbtxt
	|  |_ object_detect_inference.py
	|  |_ box_list.py
	|  |_ box_list_ops.py
	|  |_ label_map_util.py
	|  |_ ops.py
	|  |_ shape_utils.py
	|  |_ standard_fields.py
	|  |_ static_shape.py
	|  |_ string_int_label_map_pb2.py
	|_ object-detect.conf
	|_ object-detect-cpu.Dockerfile

## UAI Inference Example
The main file object_detect_inference.py contains the main class ObjectDetectModel, implementing TFAiUcloudModel, has 2 methods:

1. load\_model(self), which loads the given object detection model. 

2. execute(self, data, batch_size), which handles the inference requests. The django server will invoke MnistModel->execute when it receive requests. It will process the input 'data' array one by one which load the image from data[x] and invokes object detect to generate the result list. 

### Define the Config File
We need to provide the config file to tell the UAI Inference system to get the basic information to load the ObjectDetectModel. The config file should include following info:

1. "exec" tells which file is used as the entry-point of the user-defined inference logic and which main class is used. 
2. "tensorflow" tells which model related info should be loaded by UAI Inference system.

You can find the example config file: object-detect.conf

### Packing Inference Docker
We provide object-detect-cpu.Dockerfile for you to build local inference docker image:

	FROM uhub.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-16.04_python-2.7_tensorflow-1.7.0:v1.2

	EXPOSE 8080
	ADD ./code/ /ai-ucloud-client-django/
	ADD ./object-detect.conf  /ai-ucloud-client-django/conf.json
	ENV UAI_SERVICE_CONFIG /ai-ucloud-client-django/conf.json
	CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi

The dockerfile commands performs several operations:
1. build the docker image based on UCloud AI Inference Docker base image. (Change it into 'uhub.service.ucloud.cn' if you are using a UCloud Cloud VM, otherwise ignore everything in this bracket if you have no idea what I am talking about)
2. EXPOSE 8080 port for http service
3. ADD all code under ./code into /ai-ucloud-client-django/. (Note the root path when the django server start is /ai-ucloud-client-django/)
4. ADD the conf.json into /ai-ucloud-client-django/, The django server will automatically load a json config file to get all running info. For more details of how json file is organized please refer: [Define the Config File](#define-the-config-file)
5. Set the UAI_SERVICE_CONFIG environment to tell django server to load the config file named 'conf.json'.
6. use gunicorn to run the server.

### Build Your Own Inference Docker
With the above docker file we can now build your own inference docker image(Your directory should looks like [Setup](#setup)):

	sudo docker build -t object-detect-infer:test -f object-detect-cpu.Dockerfile .

### Run Object Detect Inference Service Locally
You can run the mnist-inference cpu server as:

	sudo docker run -it -p 8080:8080 object-detect-infer:test

### Test Object Detect Inference Service Locally
You can test the mnist-inference server as:

	curl -X POST http://localhost:8080/service -T ${PATH/TOY/YOUR/TESTCASE/DIR/}Persian_cat_1.jpeg

## Deploy Object Detect Inference Service into UAI Inference Platform
Please refer to https://docs.ucloud.cn/ai/uai-inference/index for more details. You can build the docker image build in [Build](#build-your-own-inference-docker) with another tag, or just re-tag the old one.
