# Retrain Example
This example show how to run image captioning inference on models trained with retrain method, based on UAI Inference Platform.

## Origin
This example is originally formed from the im2txt project: 
https://github.com/tensorflow/models/tree/master/research/im2txt, and uses the trained model to do image captioning. 

## Intro
UAI Inference platform can serve inference services through HTTP requests. We provide the basic docker image containing a django server which can load the user-defined inference module to do the service. To implement an inference module, you only need to implement two funcs for an inference class: load_model and execute, without understanding how django server works or installing any machine learning modules on your local host. For more details please refer to https://docs.ucloud.cn/ai/uai-inference/guide/principle.

In this example, we provide the inference service example: Im2txtModel which accepts one image and gives the captioning result, implemented in code/im2txt_inference.py.

## Setup
Acquire the Inception v3 model, and sufficient number of images and captions. Refer to: https://github.com/ucloud/uai-sdk/tree/master/examples/tensorflow/train/im2txt for training a model of self-sourced dataset.

As soon as you finished retraining a captioning model, get the output model files, and put the model file into one directory:

	/data/im2txt/
	|_ code
	|  |_ checkpoint_dir
	|  |  |_ checkpoint
  |  |  |_ model.ckpt-3000000.data-00000-of-00001
  |  |  |_ model.ckpt-3000000.meta
  |  |  |_ model.ckpt-3000000.index
  |  |  |_ word_counts.txt
	|  |_ im2txt_inference.py
	|  |_ im2txt_conf.py
  |  |_ configuration.py
  |  |_ inference_wrapper.py
  |  |_ show_and_tell_model.py
  |  |_ inference_utils
  |  |_ ops
	|_ im2txt.conf
	|_ im2txt-infer-cpu.Dockerfile

## UAI Inference Introduction
The main file retrain_inference.py contains the main class Im2txtModel, implementing TFAiUcloudModel, has 2 methods:

1. load_model(self), which loads the given im2txt model. 

2. execute(self, data, batch_size), which handles the inference requests. The django server will invoke Im2txtModel->execute when it receives requests. It will process the input 'data' array one by one, load the image from data[x] and then invoke im2txt model to generate the captioned result. The data array is the list of input images. 

The im2txt_conf.py contains a class that handles config file input. We need to implement our own class Im2txtJsonConfLoader as a subclass of the TFJSonConfLoader so we can receive specified parameters for this captioning task. If you wish to add new parameters, adjust the im2txt_conf, or inherit it into a new subclass, or you can import uai.arch_conf.tf_conf and inherit TFJSonConfLoader.

### Define the Config File
We need to provide a config file to feed parameters into the UAI Inference system. The config file includes following info:

1. "exec" part tells which file is used as the entry-point of the user-defined inference logic and which main class is used. 
2. "tensorflow" tells which model related info should be loaded by UAI Inference system, model checkpoint and the input images' size of model. Defaultly for an Inception v3 model, the size is 299 * 299.

eventually, the conf file is in the form of:
	
	{
	    "http_server" : {
	        "exec" : {
	            "main_class": "Im2txtModel",
	            "main_file": "im2txt_inference"
	        },
	        "tensorflow" : {
		    "model_dir" : "./checkpoint_dir",
        "checkpoint" : 3000000
		    "input_width" : 299,
		    "input_height" : 299
	        }
	    }
	}

You can find the example config file: im2txt.conf. Check if this file is under the directory listed above.

### Packing Inference Docker
We provide caption-infer-cpu.Dockerfile for you to build inference docker image:

	FROM uhub.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-16.04_python-2.7_tensorflow-1.7.0:v1.2

	EXPOSE 8080
	ADD ./code/ /ai-ucloud-client-django/
	ADD ./im2txt.conf  /ai-ucloud-client-django/conf.json
	ENV UAI_SERVICE_CONFIG /ai-ucloud-client-django/conf.json
	CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi

The dockerfile commands performs several operations:
1. get UCloud AI Inference Docker base image to start building the docker. This is an image of a docker containing tensorflow modules (Change the prefix into 'uhub.service.ucloud.cn' if you are using a UCloud Cloud VM, otherwise just leave it be)
2. EXPOSE 8080 port for http service
3. ADD all code under ./code into /ai-ucloud-client-django/. (Note the root path when the django server start is /ai-ucloud-client-django/)
4. ADD the conf.json into /ai-ucloud-client-django/, The django server will automatically load the json config file to get all running info. For more details of how json file is organized please refer to: [Define the Config File](#define-the-config-file)
5. Set the UAI_SERVICE_CONFIG environment to tell django server to load the config file named 'conf.json'.
6. use gunicorn to run the server.

It's alright to ignore these details, but you should ensure these files are in the correct directory.

### Build Your Own Inference Docker
With the above docker file we can now build your own inference docker image(Your directory should look like [Setup](#setup)):

  sudo docker build -t im2txt:test -f im2txt-infer-cpu.Dockerfile .

Note here we use the foresaid docker file and do not miss the dot at the end.

### Run Inference from Docker Locally
You can run the im2txt captioning server as:

	sudo docker run -it -p 8080:8080 im2txt:test

The inference server is up and running. It initializes the Im2txtModel class, and runs the load_model() function. Now it waits http POST requests from localhost 8080 port and returns a caption-probability pair lists.

### Test Retrained Captioning Inference Service Locally
Get a picture of something you want to classify. You can test the im2txt-inference server as:

	curl -X POST http://localhost:8080/service -T man-ski-in-ocean.jpg

This sends a request of POST with a picture of a man skiing in ocean. The Docker receives the picture, runs Im2txtModel.execute(data=image), during which the image data goes through the trained model, and returns the probability list to the http request sender.

## Deploy Retrained Im2txt Inference Service into UAI Inference Platform
Please refer to https://docs.ucloud.cn/ai/uai-inference/index for more details. You can build the docker image build in [Build](#build-your-own-inference-docker) with another tag, or just re-tag the old one.
