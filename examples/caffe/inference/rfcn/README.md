# py-rfcn Example
R-FCN: Object Detection via Region-based Fully Convolutional Networks

This example follows hhttps://github.com/YuwenXiong/py-R-FCN and provides examples to run py-RFCN inference based on UAI Inference Platform.

## Intro
UAI Inference platform can serve inference services through HTTP requests. We provide the basic docker image containing a django server which can load the user-defined inference module to do the service. To implement a inference module, you only need to implement two funcs: load\_model and execute. For more details please refer to https://docs.ucloud.cn/ai/uai-inference/guide/principle.

In this example, we provide the inference service example: RFCNModel which accepts one image and gives bounding boxes of detected objects.

## Setup
### Get code&model
You should follow https://github.com/rbgirshick/py-faster-rcnn/ or https://github.com/ucloud/uai-sdk/tree/master/examples/caffe/train/rfcn to train your won rfcn model. You should prepare the .caffemodel as well as the .prototxt file.

We put all files into one directory (We use ResNet-101/rfcn_end2end/ as an example):

	/data/rfcn/inference/
	|_ rfcn_models
	|  |_ test_agnostic.prototxt
	|  |_ resnet101_rfcn_final.caffemodel
	|_ __init__.py
	|_ rfcn_inference.py
	|_ rfcn.conf
	|_ rfcn-gpu.Dockerfile

### Getting py-R-FCN inference base image
UCloud provide basic py-R-FCN inference docker images through uhub.service.ucloud.cn/uaishare/gpu_uaiservice_ubuntu-14.04_python-2.7.6_caffe-py-rfcn:v1.0. You can download this docker after register a UCloud account.

The image includes:

  - cudnn6.0+cuda8.0
  - YuwenXiong/py-R-FCN
  - Microsoft caffe
  - uai sdk
  - uai inference django server

py-faster-rcnn's location in the image: /root/caffe-py-rfcn/

Caffe's location in the image: /root/caffe-py-rfcn/caffe/

Uai django server's location in the image: /ai-ucloud-client-django/

## UAI Inference Example
We provide rfcn\_inference.py which implements RFCNModel. For RFCNModel, it implements two funcs:

1. load\_model(self), which loads the RFCN model. We hardcode the model file name in load\_model in this example, you can change it if wanted. 

2. execute(self, data, batch_size), which handles the inference requests. The django server will invoke RFCNModel->execute when it receive requests. It will process the input 'data' array one by one which load the image from data[x] and invokes rfcn detect to generate the result list. 

### Define the Config File
We need to provide the config file to tell the UAI Inference system to get the basic information to load the RFCNModel. The config file should include following info:

1. "exec.main_file" tells which file is used as the entry-point of the user-defined inference logic （e.g., tools.rfcn_inference).
2. "exec.main_class" tells which main class is used (e.g., RFCNModel).

### Packing Inference Docker
We provide rfcn-gpu.Dockerfile for you to build local inference docker image.

	FROM uhub.service.ucloud.cn/uaishare/gpu_uaiservice_ubuntu-14.04_python-2.7.6_caffe-py-rfcn:v1.0

	EXPOSE 8080

	ADD ./rfcn_inference.py /ai-ucloud-client-django/tools/rfcn_inference.py
	ADD ./__init__.py /ai-ucloud-client-django/tools/__init__.py
	ADD ./rfcn_models/ /ai-ucloud-client-django/models/
	COPY ./rfcn.conf /ai-ucloud-client-django/conf.json

	RUN cp -fr /root/caffe-py-rfcn/lib /ai-ucloud-client-django/lib/
	RUN cp /root/caffe-py-rfcn/tools/_init_paths.py /ai-ucloud-client-django/tools/

	ENV UAI_SERVICE_CONFIG "conf.json"

	CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi

1. build the docker image based on UCloud AI Inference Docker base image. (Note if you are using UCloud VM you can use 'uhub.service.ucloud.cn' otherwise you should change it into 'uhub.ucloud.cn'
2. EXPOSE 8080 port for http service
3. ADD rfcn_inference.py, \_\_init\_\_.py into /ai-ucloud-client-django/tools/, the root path when the django server start is /ai-ucloud-client-django/, and the rfcn_inference python module is imported as tools.rfcn_inference. (See rfcn.conf for more detail)
4. ADD rfcn models into /ai-ucloud-client-django/models/
5. ADD the conf.json into /ai-ucloud-client-django/, The django server will automatically load a json config file to get all running info. For more details of how json file is organized please refer: [Define the Config File](#define-the-config-file)
6. copy rfcn related libs from pre-buildin caffe-py-rfcn/lib into /ai-ucloud-client-django/
7. copy all inference related files from pre-buildin caffe-py-rfcn/tools dir into /ai-ucloud-client-django/
8. Set the UAI_SERVICE_CONFIG environment to tell django server to load the config file named 'conf.json'
9. use gunicorn to run the server

### Build Your Own Inference Docker
With the above docker file we can now build your own inference docker image(Your directory should looks like [Setup](#setup)):

	sudo docker build -t rfcn-inference-gpu:test -f rfcn-gpu.Dockerfile .

### Run RFCN Inference Service Locally
You can run the rfcn-inference gpu server as:

	sudo nvidia-docker run -it -p 8080:8080 rfcn-inference-gpu:test

### Test RFCN Inference Service Locally
You can test the rfcn-inference server as:

	curl -X POST http://localhost:8080/service -T xxx.jpeg

## Deploy Mnist Inference Service into UAI Inference Platform
Please refer to https://docs.ucloud.cn/ai/uai-inference/index for more details. You can directly use the docker image build in [Build](#build-your-own-inference-docker)