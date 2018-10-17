# EAST Inference Example
This example shows how to use EAST to do text detection inference. Here we show how to build a text detection inference service based on UAI Inference system. We assume you have already known how to train an EAST model (https://github.com/argman/EAST or https://github.com/ucloud/uai-sdk/tree/master/examples/tensorflow/train/east).

## 1 Intro
UAI Inference platform can serve inference services through HTTP requests. We provide the basic docker image containing a django server which can load the user-defined inference module to do the service. To implement a inference module, you only need to implement two funcs: load\_model and execute. For more details please refer to https://docs.ucloud.cn/ai/uai-inference/guide/principle.

In this example, we provide two inference service implementations of EAST online inference examples:
1. Inference code for EAST model trained in single-node mode which is compatable with examples/tensorflow/train/east/multigpu\_train.py. It can also use the pretrained-model provided by https://github.com/argman/EAST.
2. Inference code for EAST model trained in distributed mode which is compatable with examples/tensorflow/train/east/distgpu\_train.py.

Both implementations accept a 'text' image and return a list of detected boxes.

## 2 Setup
You should download the current directory into your work place. You should also train a EAST model (https://github.com/argman/EAST or https://github.com/ucloud/uai-sdk/tree/master/examples/tensorflow/train/east) or download one from https://github.com/argman/EAST, and put it under the code/checkpoint\_dir/ directory.

We put all these files into one directory:

	/data/east/inference/
	|_ code
	|  |_ lanms
	|  |_ nets
	|  |_ data_util.py
	|  |_ east_inference.py
	|  |_ east_multi_infer.py
	|  |_ east_multi_inference.py
	|  |_ icdar.py
	|  |_ model.py
	|  |_ checkpoint_dir
	|  |  |_ checkpoint
	|  |  |_ model.ckpt-xxx
	|  |  |_ model.ckpt-xxx.index
	|  |  |_ model.ckpt-xxx.meta
	|_ east.conf
	|_ east-cpu.Dockerfile
	|_ east-gpu.Dockerfile
	|_ east-dist.conf
	|_ east-dist-gpu.Dockerfile

## 3 Inference with single-node EAST training model
### 3.1 Writing Service Code
We provide east\_inference.py which implements EASTTextDetectModel. For EASTTextDetectModel, it implements two funcs:

1. load\_model(self), which loads the EAST model from checkpoint\_dir. It first load the graph defination an then restore the model.

2. execute(self, data, batch_size), which handles the inference requests. The django server will invoke EASTTextDetectModel->execute when it receives requests. It will buffer requests into a array named 'data' when possible. In execute(), it first preprocesses the input 'data' array by invoking self.resize_image() for each data[i] and merge all preprocessed images into one batch, then calculates the image score and geometry. After getting the score and geometry, it will 'detecting' the text boxes for each request one by one. It formats resulting boxes into list object. (You can format it into json also)

### 3.2 Define the Config File
We need to provide the config file to tell the UAI Inference system to get the basic information to load the EASTTextDetectModel and the EAST model. The config file should include following info:

1. "exec" tells which file is used as the entry-point of the user-defined inference logic and which main class is used. 
2. "tensorflow" tells which model related info should be parsed by UAI Inference system.

You can find the example config file of: east.conf

### 3.3 Packing Inference Docker
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

**We also provide east-gpu.Dockerfile to help you build the GPU docker image. It acts same as east-cpu.Dockerfile except using a different base image**

### 3.4 Build Your Own Inference Docker
With the above docker file we can now build your own inference docker image(Your directory should looks like [Setup](#setup)):

	sudo docker build -t east-inference:test -f east-cpu.Dockerfile .

	sudo docker build -t east-inference-gpu:test -f east-gpu.Dockerfile .

### 3.5 Run EAST Inference Service Locally
You can run the east-inference cpu server as:

	sudo docker run -it -p 8080:8080 east-inference:test

You can run the east-inference gpu server as:

	sudo nvidia-docker run -it -p 8080:8080 east-inference-gpu:test

### 3.6 Test EAST Inference Service Locally
You can test the east-inference server as:

	curl -X POST http://localhost:8080/service -T xxx.jpeg

## 4 Inference with distributed-trained EAST model
We provide implementation of inference code compatable with the distributed-trained EAST model (Please refer to https://github.com/ucloud/uai-sdk/tree/master/examples/tensorflow/train/east for more details). It takes two steps to build a inference service:
1. export the model checkpoint into a .pb file

2. use .pb file to initialize a inference service

### 4.1 Generating .pb file
We provide east\_multi\_infer.py for you to generate .pb model file(Which is compatable with tfserve). You can run the following command to generate it:

	python east_multi_infer.py
	cp -r ./checkpoint_dir/<timestemp>/* ./checkpoint_dir/

Pay attention to the py-modules east\_multi\_infer.py required (including basic east realted modules such as model, icdar, etc.), you should put them in the same dir as east\_multi\_infer.py. Also you should put the checkpoint files into ./checkpoint\_dir.

The resulting .pb file and the corresponding variables files are located under ./checkpoint\_dir/

### 4.2 Writing Service Code
We provide the example service code in east\_multi\_inference.py. We defined EASTTextDetectModel which derived from TFAiUcloudModel.

In EASTTextDetectModel, we implement load\_model func and execute func:

1. load_model(self), which loads the crnn model by invoking east\_multi\_infer.EastPredictor('./checkpoint_dir'). We should put the checkpoint files into checkpoint\_dir.

2. execute(self, data, batch_size) which will do the inference. The django server will invoke EASTTextDetectModel->execute when it receives requests. It will buffer requests into a array named 'data' when possible. In execute(), it will call the eastPredictor to format the images and do the inference call. You can refer to east\_multi\_infer.py for more details. At last, execute() formats result into list object. (You can format it into json also)

### 4.3 Preparing model
You can use the model you trained on UAI Train Platform. Please following the example in examples/tensorflow/train/east/distgpu\_train.py (The distributed version) You should also convert the .ckpt model into .pb model according to [Generating .pb file](#generating-pb-file)

### 4.4 Preparing directory
We put all these files into one directory:
```
	/data/east/inference/
	|_ code
	|  |_ lanms
	|  |_ nets
	|  |_ data_util.py
	|  |_ east_inference.py
	|  |_ east_multi_infer.py
	|  |_ east_multi_inference.py
	|  |_ icdar.py
	|  |_ model.py
	|  |_ checkpoint_dir
    |  |  |_ saved_model.pb
    |  |  |_ variables/
	|  |  |_ ...
	|_ east-dist.conf
	|_ east-dist-gpu.Dockerfile
```
You should put .pb files under code/checkpoint\_dir/

### 4.5 Build Your Own Inference Docker
With the above docker file you can now build your own inference docker image.
```
sudo docker build -t uhub.service.ucloud.cn/YOUR_UHUB_REGISTRY/east-infer:v1.0 -f east-dist-gpu.Dockerfile .
```

Node: The docker-image generated is gpu version. You can build a cpu version as well.

### 4.6 Run EAST Inference Service 
#### You can run the east-inference gpu server Locally as:
```
sudo nvidia-docker run -it -p 8080:8080 uhub.service.ucloud.cn/YOUR_UHUB_REGISTRY/eeast-infer:v1.0
```

#### Test EAST Inference Service Locally
You can test the east-inference server as:
```
curl -X POST http://localhost:8080/service -T xxx.jpg
```

## 5 Deploy EAST Inference Service into UAI Inference Platform
Please refer to https://docs.ucloud.cn/ai/uai-inference/index for more details. You can directly use the docker image build in this example.
