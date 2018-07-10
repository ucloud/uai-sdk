# Retrain Example
This example show how to run inference of models trained with retrain method, based on UAI Inference Platform.

## Origin
This example is originally formed from the retraining project: https://www.tensorflow.org/hub/tutorials/image_retraining, and extends it by using the model trained to do object identification.

## Intro
UAI Inference platform can serve inference services through HTTP requests. We provide the basic docker image containing a django server which can load the user-defined inference module to do the service. To implement a inference module, you only need to implement two funcs: load\_model and execute. For more details please refer to https://docs.ucloud.cn/ai/uai-inference/guide/principle.

In this example, we provide the inference service example: RetrainDetectModel which accepts one image and gives object detection result.

## Setup
Acquire a retrain classification model with images of the categorical objects you wish to detect. Refer to: https://github.com/ucloud/uai-sdk/tree/master/examples/tensorflow/train/retrain for training a model of self-sourced dataset.

We put all these files into one directory:

	/data/object-detect/
	|_ code
	|  |_ checkpoint_dir
	|  |  |_ frozen_inference_graph.pb
	|  |  |_ label_map.pbtxt
	|  |_ retrain_inference.py
  |  |_ retrain_conf.py
	|_ retrain-detect.conf
	|_ retrain-detect-cpu.Dockerfile

## UAI Inference Example
The main file object_detect_inference.py contains the main class ObjectDetectModel, implementing TFAiUcloudModel, has 2 methods:

1. load\_model(self), which loads the given retrain detection model. 

2. execute(self, data, batch_size), which handles the inference requests. The django server will invoke RetrainDetectModel->execute when it receive requests. It will process the input 'data' array one by one which load the image from data[x] and invokes object detect to generate the result list. 

### Define the Config File
We need to provide the config file to tell the UAI Inference system to get the basic information to load the RetrainDetectModel. The config file should include following info:

1. "exec" tells which file is used as the entry-point of the user-defined inference logic and which main class is used. 
2. "tensorflow" tells which model related info should be loaded by UAI Inference system.

You can find the example config file: retrain-detect.conf. Put these 2 files under the directory listed above.

### Packing Inference Docker
We provide retrain-detect-cpu.Dockerfile for you to build local inference docker image:

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

	sudo docker build -t retrain-infer:test -f retrain-detect-cpu.Dockerfile .

### Run Object Detect Inference Service Locally
You can run the retrain-inference cpu server as:

	sudo docker run -it -p 8080:8080 object-detect-infer:test

### Test Object Detect Inference Service Locally
You can test the retrain-inference server as:

	curl -X POST http://localhost:8080/service -T ${PATH/TOY/YOUR/TESTCASE/DIR/}Persian_cat_1.jpeg

## Deploy Object Detect Inference Service into UAI Inference Platform
Please refer to https://docs.ucloud.cn/ai/uai-inference/index for more details. You can build the docker image build in [Build](#build-your-own-inference-docker) with another tag, or just re-tag the old one.
