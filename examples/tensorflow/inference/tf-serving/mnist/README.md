# Mnist Inference Serving Example
This example shows how to generate a tf-serving capable model and run the mnist inference service using this model based on UAI Inference Docker.

## Build Mnist tf-serving model
Use mnist_saved_model.py to generate tf-serving capable model. Please refer to https://github.com/tensorflow/serving/blob/master/tensorflow_serving/example/mnist_saved_model.py for more details.

It uses the tf.saved_model.builder.SavedModelBuilder.save() to generate a tf-serving capable model

## Build Mnist Inference Service with UAI Inference toolkit
Building a mnist inference service docker need some preparations:

1. Write a simple Inference class to load the model, process the data, and run the inference logic.
2. Provide a config file to tell UAI Inference system where to load the model
3. Get the basic UAI Inference docker base image

For more details please refer to https://docs.ucloud.cn/ai/uai-inference/index

### Writing Service Code
We provide the example service code in inference.py. We defined MnistModel which derived from TFServingAiUcloudModel. TFServingAiUcloudModel has implemented the generic logic of loading tf-serving capable model as well as the logic of doing the inference (with a default feature of autobatching).

In MnistModel we need to implement two funcs:

1. preprocess(self, data) which preprocess the input data and convert it into numpy capable data. In this example, it will do some reshape and normalization operations.
2. execute(self, data, batch_size) which will do the inference. We only need to call the TFServingAiUcloudModel.execute func to process the input 'data' array and get the result list: output_tensor. And the we format the output into string arrays. (You can format it into json also)

### Define the Config File
We need to provide the config file to tell the UAI Inference system to get the basic information to load the tf-serving capable model. The config file should include following info:

1. "exec" tells which file is used as the entry-point of the user-defined inference logic and which main class is used. 
2. "tensorflow" tells which model related info should be parsed by UAI Inference system.

The config file in this example is as follow:

    "http_server" : {
        "exec" : {
            "main_class": "MnistModel",
            "main_file": "inference"
        },
        "tensorflow" : {
            "model_dir" : "./checkpoint_dir/",
            "tag": ["serve"],
            "signature": "predict_images",
            "input": {
                "name": "images"
            },
            "output": {
                "name": ["scores"]
            }
        }
    }
    
The entry-point file module is inference (Note we must omit the .py suffix). The user-defined inference main class is MnistModel.

It provides several info for the system to load the model. These infos are necessary to load a tf-serving capable module which is usually a protobuf file e.g. checkpoint_dir/saved_model.pb：

1. model_dir: tell where to find the model file
2. tag: tell which graph to load from the model file, it should be "serve" here as compatable with tf.saved_model.tag_constants.SERVING. (For more details please see: https://github.com/tensorflow/tensorflow/blob/master/tensorflow/python/saved_model/tag_constants.py)
3. signature: the signature when building the model: see L127 in mnist_saved_model.py, the builder add_meta_graph_and_variables into the graph defining the input and the output with the signature of 'predict_images'
4. input: tell the input tensor name: see L122 in mnist_saved_model.py
5. output: tell the output tensor name: see L123 in mnist_saved_model.py

### Build the docker image
We build the minst service docker image based on UCloud AI Inference Docker base image: uhub.service.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-14.04_python-2.7.6_tensorflow-1.4.0:v1.1, you can get it by:

    # In UCloud VM
    sudo docker pull uhub.service.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-14.04_python-2.7.6_tensorflow-1.4.0:v1.1
    
    # Internet
    sudo docker pull uhub.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-14.04_python-2.7.6_tensorflow-1.4.0:v1.1
    
#### Preparing code and model
We have provide the example inference code (mnist/inference.py) and checkpoint files (inside mnist/checkpoint_dir/). We also prepare the config file conf.json. You should put them together into mnist/ directory.

    # ls
    mnist
    # ls mnist
    checkpoint_dir conf.json inference.py

#### Preparing dockerfile
We provide the example dockerfile to pack the inference service docker image. You should put it into the same directory with the mnist package.

	# ls
	mnist/ uaiservice.Dockerfile
	
The dockerfile(uaiservice.Dockerfile) include following contents:

    FROM  uhub.service.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-14.04_python-2.7.6_tensorflow-1.4.0:v1.1

    EXPOSE 8080
    ADD ./mnist /ai-ucloud-client-django/
    ADD ./mnist/conf.json  /ai-ucloud-client-django/conf.json
    ENV UAI_SERVICE_CONFIG /ai-ucloud-client-django/conf.json
    CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi

1. build the docker image based on UCloud AI Inference Docker base image. (Note if you are using UCloud VM you can use 'uhub.service.ucloud.cn' otherwise you should change it into 'uhub.ucloud.cn'
2. EXPOSE 8080 port for http service
3. ADD all code under mnist into /ai-ucloud-client-django/. (Note the root path when the django server start is /ai-ucloud-client-django/)
4. ADD the conf.json into /ai-ucloud-client-django/, The django server will automatically load a json config file to get all running info. For more details of how json file is organized please refer: [Define the Config File](###define-the-config-file)
5. Set the UAI_SERVICE_CONFIG environment to tell django server to load the config file named 'conf.json'
6. use gunicorn to run the server

#### Build your own service docker
With the above docker file we can now build our own service docker image:

    sudo docker build -t mnist-serve:test -f uaiservice.Dockerfile .

#### Run and Test
We can run the server directly:

    sudo docker run -it -p 8080:8080 mnist-serve:test
    
Then we can test it by:

     curl -X POST http://127.0.0.1:8080/service -T <img>

### Deploy to UAI Inference Platform
Please refer to https://docs.ucloud.cn/ai/uai-inference/index for more details
