# ArcFace Example
This example shows how to run insightface/ArcFace inference on UAI Platform. The example provides a implementation of setting up an insightface inference service using UAI Inference server template. This example follows the implementation in https://github.com/deepinsight/insightface as well as examples/mxnet/insightface/train/

## Intro
UAI Inference platform can serve inference services through HTTP requests. We provide the basic docker image containing a django server which can load the user-defined inference module to do the service. To implement a inference module, you only need to implement two funcs: load\_model and execute. For more details please refer to https://docs.ucloud.cn/ai/uai-inference/guide/principle.

In this example, we provide InsightFaceModel, which accept 'one' face image and return the embedding.

## Setup
You should download the current directory into your work place. You should donwload the insightface code from https://github.com/deepinsight/insightface and put an ArcFace model under your work place. 

We put all these files into one directory:

	/example/insightface/inference/
	|_ code
	|  |_ insightface_infer.py
	|  |_ checkpoint_dir
	|  |  |_ model-r100-aceFace-0003.params  
	|  |  |_ model-r100-aceFace-1-0003.params  
	|  |  |_ model-r100-aceFace-2-0003.params  
	|  |  |_ model-r100-aceFace-3-0003.params  
	|  |  |_ model-r100-aceFace-symbol.json
	|  insightface
	|  |_ src
	|  |_ ...
	
In this example we use the model file trained using 4 nodes (For more details of running insightface training in a distributed environment please refer to examples/mxnet/insightface/train/).

## UAI Inference Example
We provide insightface\_infer.py which implements InsightFaceModel, it includes two funcs:

1. load\_model(self), which loads the FaceNet model from checkpoint\_dir. 

2. execute(self, data, batch_size), which handles the inference requests. The django server will invoke InsightFaceModel->execute when it receive requests.

### Define the Config File
We need to provide the config file to tell the UAI Inference system to get the basic information to load the model. The config file should include following info:

1. "exec" tells which file is used as the entry-point of the user-defined inference logic and which main class is used. 
2. "mxnet" tells which model related info should be parsed by UAI Inference system, which includes the relative path of where the model is stored, the name of the model and the epoch number.

You can find the example config file as insightface_infer.conf

### Selecting GPU/CPU inference
As MXNet use context to define the default running device, you should change the code in insightface\_infer.py to set the right device:

	# Line 100
	ctx = mx.cpu()
    # ctx = mx.gpu()

The default device we use is CPU.

### Packing Inference Docker
We provide insightface\_infer\_cpu.Dockerfile, insightface\_infer\_gpu.Dockerfile. Take insightface\_infer\_cpu.Dockerfile as an example:

	FROM uhub.service.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-14.04_python-2.7.6_mxnet-1.0.0:v1.2
	
	EXPOSE 8080
	ADD ./code/ /ai-ucloud-client-django/
	ADD ./insightface/deploy/mtcnn_detector.py /ai-ucloud-client-django/
	ADD ./insightface/deploy/helper.py /ai-ucloud-client-django/
	ADD ./insightface/deploy/mtcnn-model/ /ai-ucloud-client-django/mtcnn-model/
	ADD ./insightface/src/common/ /ai-ucloud-client-django/common/
	ADD ./insightface_infer.conf  /ai-ucloud-client-django/conf.json
	ENV UAI_SERVICE_CONFIG /ai-ucloud-client-django/conf.json
	CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi
	
1. build the docker image based on UCloud AI Inference Docker base image. (Note if you are using UCloud VM you can use 'uhub.service.ucloud.cn' otherwise you should change it into 'uhub.ucloud.cn'
2. EXPOSE 8080 port for http service
3. ADD all code as well as the model under ./code into /ai-ucloud-client-django/. (Note the root path when the django server start is /ai-ucloud-client-django/)
4. Copy mtcnn\_detector related code into /ai-ucloud-client-django/.
5. ADD the conf.json into /ai-ucloud-client-django/, The django server will automatically load a json config file to get all running info. For more details of how json file is organized please refer: [Define the Config File](#define-the-config-file)
6. Set the UAI_SERVICE_CONFIG environment to tell django server to load the config file named 'conf.json'
7. use gunicorn to run the server

### Build Your Own Inference Docker
With the above docker file we can now build your own inference docker image(Your directory should looks like [Setup](#setup)):

    sudo docker build -t insightface_infer:test -f insightface_infer_cpu.Dockerfile .
    
### Run InsightFace Inference Service Locally
We can run the insightface feature inference server as

    sudo docker run -it -p 8080:8080 insightface_infer:test

### Test InsightFace Inference Service Locally
You can run the following cmd to test the server

	curl -X POST http://localhost:8080/service -T xxx.jpeg
	
## Deploy InsightFace Inference Service into UAI Inference Platform
Please refer to https://docs.ucloud.cn/ai/uai-inference/index for more details. You can directly use the docker image build in [Build](#build-your-own-inference-docker)