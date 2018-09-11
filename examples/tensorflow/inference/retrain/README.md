# Retrain Example
This example show how to run object classification inference on models trained with retrain method, based on UAI Inference Platform.

## Origin
This example is originally formed from the retraining project: https://www.tensorflow.org/hub/tutorials/image_retraining, and uses the retrained model to do new object classification. 

## Intro
UAI Inference platform can serve inference services through HTTP requests. We provide the basic docker image containing a django server which can load the user-defined inference module to do the service. To implement an inference module, you only need to implement two funcs for an inference class: load_model and execute, without understanding how django server works or installing any machine learning modules on your local host. For more details please refer to https://docs.ucloud.cn/ai/uai-inference/guide/principle.

In this example, we provide the inference service example: RetrainedClassificationModel which accepts one image and gives object classification result, implemented in code/retrain_inference.py.

## Setup
Acquire an object classification model, and sufficient number of images of the categorical objects you wish to classify. Refer to: https://github.com/ucloud/uai-sdk/tree/master/examples/tensorflow/train/retrain for training a model of self-sourced dataset. It is suggested to retrieve label map file while training(there is a parameter that controls this option), so we can get the object types, instead of indices, when inferencing.

As soon as you finished retraining a classification model, get the output graph and rename it to frozen_inference_graph.pb, put the model file and label file into one directory:

	/data/retrain/
	|_ code
	|  |_ checkpoint_dir
	|  |  |_ frozen_inference_graph.pb
	|  |  |_ label_map.pbtxt
	|  |_ retrain_inference.py
	|  |_ retrain_conf.py
	|_ retrained-classification.conf
	|_ retrained-classification-cpu.Dockerfile

## UAI Inference Introduction
The main file retrain_inference.py contains the main class RetrainedClassificationModel, implementing TFAiUcloudModel, has 2 methods:

1. load_model(self), which loads the given retrained classification model. 

2. execute(self, data, batch_size), which handles the inference requests. The django server will invoke RetrainedClassificationModel->execute when it receives requests. It will process the input 'data' array one by one, load the image from data[x] and then invoke retrained object detection model to generate the result list. The data array is the list of input images. 

The retrain_conf.py contains a class that handles config file input. We need to implement our own class RetrainJsonConfLoader as a subclass of the TFJSonConfLoader so we can receive specified parameters for this classification task. If you wish to add new parameters, adjust the retrain_conf, or inherit it into a new subclass, or you can import uai.arch_conf.tf_conf and inherit TFJSonConfLoader.

### Define the Config File
We need to provide a config file to feed parameters into the UAI Inference system. The config file includes following info:

1. "exec" part tells which file is used as the entry-point of the user-defined inference logic and which main class is used. 
2. "tensorflow" tells which model related info should be loaded by UAI Inference system, model type and the input images' size of model. Commonly, if you use resnet101, the size will be 224 pixels high and 224 pixels tall. The mobilenet models indicate the input size in the model name(e.g. mobilenet_v1_1.0_224 gets an input of 224 * 224). Inception_v3 needs a 299 * 299 input. If you are not sure, look up in the model source page at https://www.tensorflow.org/hub/modules/image and find how large the input is. 

eventually, the conf file is in the form of:
	
	{
	    "http_server" : {
	        "exec" : {
	            "main_class": "RetrainedClassificationModel",
	            "main_file": "retrain_inference"
	        },
	        "tensorflow" : {
		    "model_dir" : "./checkpoint_dir",
		    "input_width" : "224",
		    "input_height" : "224"
	        }
	    }
	}

You can find the example config file: retrained-classification.conf. Check if this file is under the directory listed above.

### Packing Inference Docker
We provide retrained-classification-cpu.Dockerfile for you to build inference docker image:

	FROM uhub.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-16.04_python-2.7_tensorflow-1.7.0:v1.2

	EXPOSE 8080
	ADD ./code/ /ai-ucloud-client-django/
	ADD ./retrained-classification.conf  /ai-ucloud-client-django/conf.json
	ENV UAI_SERVICE_CONFIG /ai-ucloud-client-django/conf.json
	CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi

The dockerfile commands performs several operations:
1. get UCloud AI Inference Docker base image to start building the docker. This is an image of a docker containing tensorflow modules (Change the prefix into 'uhub.service.ucloud.cn' if you are using a UCloud Cloud VM, otherwise just leave it be)
2. EXPOSE 8080 port for http service
3. ADD all code under ./code into /ai-ucloud-client-django/. (Note the root path when the django server start is /ai-ucloud-client-django/)
4. ADD the conf.json into /ai-ucloud-client-django/, The django server will automatically load the json config file to get all running info. For more details of how json file is organized please refer to: [Define the Config File](#define-the-config-file)
5. Set the UAI_SERVICE_CONFIG environment to tell django server to load the config file named 'conf.json'.
6. use gunicorn to run the server.

It's alright to ignore these details, but you should ensure this file is in the working directory.

### Build Your Own Inference Docker
With the above docker file we can now build your own inference docker image(Your directory should looks like [Setup](#setup)):

	sudo docker build -t retrained-classification:test -f retrained-classification-cpu.Dockerfile .

Note here we use the foresaid docker file and do not miss the dot at the end.

### Run Inference from Docker Locally
You can run the retrain-inference cpu server as:

	sudo docker run -it -p 8080:8080 retrained-classification:test

The inference server is up and running. It initializes the RetrainedClassificationModel class, and runs the load_model() function. Now it waits http POST requests from localhost 8080 port and returns an object-probability pair lists.

### Test Retrained Object-classification Inference Service Locally
Get a picture of something you want to classify. You can test the retrain-inference server as:

	curl -X POST http://localhost:8080/service -T Persian_cat_1.jpeg

This sends a request of POST with a picture of Persians. The Docker receives the picture, runs RetrainedClassificationModel.execute(data=image), during which the image data goes through the trained model, and returns the probability list to the http request sender.

## Deploy Retrained Object-classification Inference Service into UAI Inference Platform
Please refer to https://docs.ucloud.cn/ai/uai-inference/index for more details. You can build the docker image build in [Build](#build-your-own-inference-docker) with another tag, or just re-tag the old one.
