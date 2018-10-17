# TF Slim Example
TF-slim is a new lightweight high-level API of TensorFlow (tensorflow.contrib.slim) for defining, training and evaluating complex models. 
In [slim-train example](https://github.com/ucloud/uai-sdk/tree/master/examples/tensorflow/train/slim/train) 
we shows how to classify our pictures data with TF-slim example code on UAI Platform. 
This example show how to run image-classification inference based on UAI Inference Platform.

Chinese version of the case introduction you can refer to https://cms.docs.ucloudadmin.com/ai/uai-train/case/slim/infer.

## 1 Intro
UAI Inference platform can serve inference services through HTTP requests. 
We provide the basic docker image containing a django server which can load the user-defined inference module to do the service. 
To implement a inference module, you only need to implement two funcs: load\_model and execute. 
For more details please refer to https://docs.ucloud.cn/ai/uai-inference/guide/principle.

In this example, we provide the inference service example: slimModel which accepts one picture and gives picture category.

## 2 Build slim Inference Service with UAI Inference toolkit
Building a slim inference service docker need some preparations:

1. Write a simple Inference class to load the model, process the data, and run the inference logic.
2. Provide a config file to tell UAI Inference system where to load the model.
3. Get the basic UAI Inference docker base image.

For more details please refer to https://docs.ucloud.cn/ai/uai-inference/index

### 2.1 Writing Service Code
We provide the example service code in sliminfer.py. We defined slimModel which derived from TFAiUcloudModel. 

In slimModel we only need to implement load_model funcs and execute funcs:

1. load_model(self),which loads the given model.   
2. execute(self, data, batch_size) which will do the inference. 
The django server will invoke slimModel->execute when it receives requests. 

### 2.2 Define the Config File
We need to provide the config file to tell the UAI Inference system to get the basic information to load  model. 

The config file is as follows:

```
{
        "http_server" : {
                "exec" : {
                        "main_class": "slimModel",
                        "main_file": "sliminfer"
                },
                "tensorflow" : {
                        "model_dir" : "/data/output"
                }
        },
       "infor" : {
          "preprocessing_name" : "None",
          "model_name" : "vgg_19",
          "eval_image_size" : "None"
        }
}
```

1  "http_server.exec" tells which file is used as the entry-point of the user-defined inference logic and which main class is used. <br>
2  "http_server.tensorflow" tells which model related info should be parsed by UAI Inference system.<br>
3  "infor.preprocessing_name" tells parameter:preprocessing_name during [model training](https://github.com/ucloud/uai-sdk/tree/master/examples/tensorflow/train/slim/train) <br>
4  "model_name" tells parameter:model_name during [model training](https://github.com/ucloud/uai-sdk/tree/master/examples/tensorflow/train/slim/train) <br>
5  "eval_image_size" tells parameter:eval_image_size during [model training](https://github.com/ucloud/uai-sdk/tree/master/examples/tensorflow/train/slim/train) <br>

## 3 Preparing model
You can use the model you trained on UAI Train Platform. 

## 4 Preparing directory

Suppose you get the slim code, you can do the following steps to build your own UAI slim image:

    $ cd ${SLIM_CODE_DIR}
    $ ls slim/
    BUILD datasets/ deployment/ ... train_image_classifier.py WORKSPACE
    $ cp ${UAI-SLIM_EXAMPLE}/slim_infer.Dockerfile .
    $ cp ${UAI-SLIM_EXAMPLE}/slim.conf .
    $ cp ${UAI-SLIM_EXAMPLE}/sliminfer.py .
	
The file structure is as follows
```
|_ slim/
|_ checkpoint_dir/
   |_ checkpoint 
   |_ info.json
   |_ labels.txt
   |_ model.ckpt...
|_ slim.conf
|_ slim_infer.Dockerfile
|_ sliminfer.py
```
Info.json and labels.txt are generated in [Generating tfrecord files](https://github.com/ucloud/uai-sdk/tree/master/examples/tensorflow/train/slim/train/README.md#Generating tfrecord files)

## 5 Build Your Own Inference Docker
With the above docker file we can now build your own inference docker image.

	$ sudo docker build -t uhub.service.ucloud.cn/<YOUR_UHUB_REGISTRY>/slim_infer -f slim_infer.Dockerfile .


## 6 Run slim Inference Service 

###  You can run the slim_infer server Locally as:
```
sudo docker run -it -p 8080:8080 uhub.service.ucloud.cn/YOUR_UHUB_REGISTRY/slim_infer
```
You can test the slim_infer server as:
```
curl -X POST http://localhost:8080/service -T /data/fer/pic/angry/00000_1.jpg
```
###  Deploy slim Inference Service into UAI Inference Platform
Please refer to https://docs.ucloud.cn/ai/uai-inference/index for more details. 
