# XGBoost Binary Classification Inference Serving Example
This example shows how to build a binary classification inference service based on UAI Inference Docker.

## Preparation
The binary classification inference serving example follows the official xgboost binary\_classification demo: https://github.com/dmlc/xgboost/tree/master/demo/binary_classification. You can follow the DEMO to generate your own mushroom classification model (e.g., 0002.model).

## Build Binary Classification Inference Service with UAI Inference
Building a binary classification inference service docker need following preparations:

1. Write a simple Inference class to load the model, process the data, and run the inference logic.
2. Provide a config file to tell UAI Inference system where to load the model
3. Generate the basic UAI Inference docker base image

For more details of UAI Inference system please refer to https://docs.ucloud.cn/ai/uai-inference/index (chinese only)

### Writing Inference Service Code
We provide the example service code in binary.py. We defined BinaryClassModel which derived from XGBoostUcloudModel. The BinaryClassModel implements two funcs:

1. load\_model(), which use xgb.Booster.load\_model() to load the xgboost model (e.g., 0002.model). Note: the model file name is loaded automatically by XGBoostUcloudModel.\_load() func and stored as self.model\_name

2. execute(): which parse the input data array and generate a csr maxtrix for xgb.Booster to predict. It should return the predict results also as an array which is compatable with the input data array

### Define the Config File
We need to provide the config file to tell the UAI Inference system to get the basic information to load the xgboost model. The config file should include following info:

1. "exec" tells which file is used as the entry-point of the user-defined inference logic and which main class is used. 
2. "xgboost" tells which model related info should be parsed by UAI Inference system.

The config file in this example is as follow:

    "http_server" : {
        "exec" : {
            "main_class": "MnistModel",
            "main_file": "mnist_inference"
        },
        "xgboost" : {
            "model_name" : "0002.model"
        }
    }
    
The entry-point file module is binary (Note we must omit the .py suffix). The user-defined inference main class is BinaryClassModel.

The target xgboost model is 0002.model which locate with the same directory with binary.py

### Build Inference Service Docker
We should build the inception inference service docker image based on UCloud AI Inference Docker base image: uhub.service.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-16.04_python-2.7.6_xgboost-0.7:v1.0 , you can get it by:

    # In UCloud VM
    sudo docker pull uhub.service.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-16.04_python-2.7.6_xgboost-0.7:v1.0
    
    # Internet
    sudo docker pull uhub.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-16.04_python-2.7.6_xgboost-0.7:v1.0

We have provided the example Dockerfile to build the binary classification inference service docker:

	FROM uhub.service.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-16.04_python-2.7.6_xgboost-0.7:v1.0

	EXPOSE 8080
	ADD ./binary_classification/ "/ai-ucloud-client-django/"
	ENV UAI_SERVICE_CONFIG /ai-ucloud-client-django/xgboost_binary.conf
	CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi

It copy the files inside binary\_classification (binary.py, xgboost\_binary.conf, 0002.model) into /ai-ucloud-client-django/ and use gunicorn to start the service.

You can use follow CMD to build the docker:

	docker build -t xgboost_binary:test -f binary.Dockerfile .

### Local Test
To run the xgboost binary classification inference service docker locally, you can run the following CMD:
	
	sudo docker run -p 8080:8080 -it xgboost_binary:test
	
The use the following CMD to test and get the result:

	# curl -X POST http://localhost:8080/service -d "0 1:1 9:1 19:1 21:1 24:1 34:1 36:1 39:1 42:1 53:1 56:1 65:1 69:1 77:1 86:1 88:1 92:1 95:1 102:1 106:1 117:1 122:1"
	
	0.0076854294