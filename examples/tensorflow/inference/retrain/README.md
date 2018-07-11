# Retrain Example
This example show how to run object classification/detection inference on models trained with retrain method, based on UAI Inference Platform.

## Origin
This example is originally formed from the retraining project: https://www.tensorflow.org/hub/tutorials/image_retraining, and extends it by using the model trained to do object classification. In this example, for convenience, object detection and object classification are equivalent, since we have a relatively similar example on object detection: https://github.com/FinchZHU/uai-sdk/edit/master/examples/tensorflow/inference/object-detect.

## Intro
UAI Inference platform can serve inference services through HTTP requests. We provide the basic docker image containing a django server which can load the user-defined inference module to do the service. To implement an inference module, you only need to implement two funcs: load\_model and execute. For more details please refer to https://docs.ucloud.cn/ai/uai-inference/guide/principle.

In this example, we provide the inference service example: RetrainDetectModel which accepts one image and gives object detection/classification result.

## Setup
Acquire an object classification model, and sufficient number of images of the categorical objects you wish to detect. Refer to: https://github.com/ucloud/uai-sdk/tree/master/examples/tensorflow/train/retrain for training a model of self-sourced dataset. It is suggested to retrieve label map file while training(there is a parameter that controls this option), so we can get the object types, instead of indices, when inferencing.

As soon as you finished retraining a detection model, get the output graph and rename it to frozen_inference_graph.pb, put the model file and label file into one directory:

	/data/retrain/
	|_ code
	|  |_ checkpoint_dir
	|  |  |_ frozen_inference_graph.pb
	|  |  |_ label_map.pbtxt
	|  |_ retrain_inference.py
	|  |_ retrain_conf.py
	|_ retrain-detect.conf
	|_ retrain-detect-cpu.Dockerfile

## UAI Inference Example
The main file retrain_inference.py contains the main class RetrainDetectModel, implementing TFAiUcloudModel, has 2 methods:

1. load\_model(self), which loads the given retrained detection model. 

2. execute(self, data, batch_size), which handles the inference requests. The django server will invoke RetrainDetectModel->execute when it receives requests. It will process the input 'data' array one by one, load the image from data[x] and then invoke retrained object detection model to generate the result list. The data array is the list of input images. 

The retrain_conf.py contains a class that handles config file input. Since we have some additional config parameters, we need this class RetrainJsonConfLoader, inheriting the regular TFJSonConfLoader, to get the new parameters. If you wish to add new parameters for this example, adjust this retrain_conf script accordingly so it is able to handle new parameters.

### Define the Config File
We need to provide the config file to tell the UAI Inference system to get the basic information to load the RetrainDetectModel. The config file should include following info:

1. "exec" tells which file is used as the entry-point of the user-defined inference logic and which main class is used. 
2. "tensorflow" tells which model related info should be loaded by UAI Inference system, model type and the input images' size of model. Commonly, if you use resnet101, the size will be 224 pixels high and 224 pixels tall. The mobilenet models indicate the input size in the model name(e.g. mobilenet_v1_1.0_224 gets an input of 224 * 224). Inception_v3 needs a 299 * 299 input. If you are not sure, look up in the model source page at https://www.tensorflow.org/hub/modules/image and find how large the input is.

You can find the example config file: retrain-detect.conf. Put these 2 files under the directory listed above.

### Packing Inference Docker
We provide retrain-detect-cpu.Dockerfile for you to build local inference docker image:

	FROM uhub.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-16.04_python-2.7_tensorflow-1.7.0:v1.2

	EXPOSE 8080
	ADD ./code/ /ai-ucloud-client-django/
	ADD ./retrain-detect.conf  /ai-ucloud-client-django/conf.json
	ENV UAI_SERVICE_CONFIG /ai-ucloud-client-django/conf.json
	CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi

The dockerfile commands performs several operations:
1. build the docker image based on UCloud AI Inference Docker base image. This is an image of a docker containing tensorflow modules (Change it into 'uhub.service.ucloud.cn' if you are using a UCloud Cloud VM, otherwise ignore everything in this bracket if you have no idea what I am talking about)
2. EXPOSE 8080 port for http service
3. ADD all code under ./code into /ai-ucloud-client-django/. (Note the root path when the django server start is /ai-ucloud-client-django/)
4. ADD the conf.json into /ai-ucloud-client-django/, The django server will automatically load a json config file to get all running info. For more details of how json file is organized please refer: [Define the Config File](#define-the-config-file)
5. Set the UAI_SERVICE_CONFIG environment to tell django server to load the config file named 'conf.json'.
6. use gunicorn to run the server.

### Build Your Own Inference Docker
With the above docker file we can now build your own inference docker image(Your directory should looks like [Setup](#setup)):

	sudo docker build -t retrain-infer:test -f retrain-detect-cpu.Dockerfile .

### Run 
ect Detect Inference Service Locally
You can run the retrain-inference cpu server as:

	sudo docker run -it -p 8080:8080 retrain-infer:test

### Test Retrained Object-classification Inference Service Locally
You can test the retrain-inference server as:

	curl -X POST http://localhost:8080/service -T ${PATH/TO/YOUR/TESTCASE/DIR/}Persian_cat_1.jpeg

## Deploy Retrained Object-classification Inference Service into UAI Inference Platform
Please refer to https://docs.ucloud.cn/ai/uai-inference/index for more details. You can build the docker image build in [Build](#build-your-own-inference-docker) with another tag, or just re-tag the old one.
