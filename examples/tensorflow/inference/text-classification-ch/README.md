# Text Classification Inference Example with CNN and RNN (Chinese)
This example shows how to use CNN/RNN to do text classification (Chinese) inference. Here we shows how to build a text classification inference service based on UAI Inference system. We assume you have already known how to train a text classificaiton model either according to https://github.com/ucloud/uai-sdk/tree/master/examples/tensorflow/train/text-classification-ch or according to https://github.com/gaussic/text-classification-cnn-rnn

## Setup
You should download the current directory into your work place.

You should also follow https://github.com/ucloud/uai-sdk/tree/master/examples/tensorflow/train/text-classification-ch to train a text classification model (CNN/RNN) and download the cnews.vocab.txt, and put them under code dir.

We put all these files into one directory:

	/data/txt/inference/
	|_ text-cnn-cpu.Dockerfile
	|_ txt_class_cnn.conf
	|_ test.txt
	|_ test2.txt
	|_ code
	|  |_ cnews_loader.py
	|  |_ cnn_model.py
	|  |_ rnn_model.py
	|  |_ txt_cnn_rnn_inference.py
	|  |_ cnews
	|  |  |_ cnews.vocab.txt
	|  |_ checkpoint_dir
	|  |  |_ checkpoint
	|  |  |_ textcnn.data-00000-of-00001
	|  |  |_ textcnn.meta
	|  |  |_ textcnn.index 

## Intro
UAI Inference platform can serve inference services through HTTP requests. We provide the basic docker image containing a django server which can load the user-defined inference module to do the service. To implement a inference module, you only need to implement two funcs: load\_model and execute. For more details please refer to https://docs.ucloud.cn/ai/uai-inference/guide/principle.

In this example we have provided the inference module implementation in txt\_cnn\_rnn\_inference.py.

### UAI Inference Example
txt\_cnn\_rnn\_inference.py provides both TxtClassCNNModel and TxtClassRNNModel for cnn model inference and rnn model inference. Here we only take CNN model as an example. 

For TxtClassCNNModel, it implements two funcs:

1. load\_model(self), which loads CNN model from checkpoint\_dir and load the vocab from cnews/cnews.vocab.txt. 

2. execute(self, data, batch_size) which handles the inference requests. The django server will invoke TxtClassCNNModel->execute when it receive requests. It will process the input 'data' array and get the result list: output_tensor. And the we format the output into string arrays. (You can format it into json also)

#### Modify checkpoint file
In both TxtClassCNNModel and TxtClassRNNModel, we use tf.train.latest_checkpoint(self.model_dir) to load the model checkpoint. It will read the 'checkpoint' file (located in ./checkpoint_dir) to get model\_checkpoint\_path and all\_model\_checkpoint\_paths. As we will changed the location of model files (.index, .meta .data-xxx), we also should modify the 'checkpoint':

	model_checkpoint_path: "textcnn"
	all_model_checkpoint_paths: "textcnn"

Here we use the related path as model files (.index, .meta .data-xxx) are in the same directory of 'checkpoint' file.

### Define the Config File
We need to provide the config file to tell the UAI Inference system to get the basic information to load the TxtClassCNNModel and the CNN model. The config file should include following info:

1. "exec" tells which file is used as the entry-point of the user-defined inference logic and which main class is used. 
2. "tensorflow" tells which model related info should be parsed by UAI Inference system.

You can find the example config file: txt\_class.conf

### Packing CNN/RNN Inference Docker
We provide text-cnn-cpu.Dockerfile for you to build the local inference docker image. The dockerfile include following contents:

	FROM uhub.service.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-16.04_python-2.7.6_tensorflow-1.6.0:v1.0

	EXPOSE 8080
	ADD ./code/ /ai-ucloud-client-django/
	ADD ./txt_class_cnn.conf  /ai-ucloud-client-django/conf.json
	ENV UAI_SERVICE_CONFIG /ai-ucloud-client-django/conf.json
	CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi

1. build the docker image based on UCloud AI Inference Docker base image. (Note if you are using UCloud VM you can use 'uhub.service.ucloud.cn' otherwise you should change it into 'uhub.ucloud.cn'
2. EXPOSE 8080 port for http service
3. ADD all code under ./code into /ai-ucloud-client-django/. (Note the root path when the django server start is /ai-ucloud-client-django/)
4. ADD the conf.json into /ai-ucloud-client-django/, The django server will automatically load a json config file to get all running info. For more details of how json file is organized please refer: [Define the Config File](#define-the-config-file)
5. Set the UAI_SERVICE_CONFIG environment to tell django server to load the config file named 'conf.json'
6. use gunicorn to run the server

#### Build Your Own Inference Docker
With the above docker file we can now build our own inference docker image(Your directory should looks like [Setup](#setup)):

    sudo docker build -t txt-class:test -f text-cnn-cpu.Dockerfile .

#### Run CNN Inference Service Locally
We can run the server directly:

    sudo docker run -it -p 8080:8080 txt-class:test

#### Test CNN Inference Service Locally
We profile the test example in test.txt and test2.txt. Then we can test service by:

	curl -X POST http://127.0.0.1:8080/service -T test.txt

#### Deploy CNN Inference Service into UAI Inference Platform
Please refer to https://docs.ucloud.cn/ai/uai-inference/index for more details. You can directly use the docker image build in [Build](#build-your-own-inference-docker)