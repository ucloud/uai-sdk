# Wide&Deep Inference Serving Example
This example shows how to generate a tf-serving capable model and run the wide&deep service using based on UAI Inference Docker.

## Build Wide&Deep tf-serving model
We provide the example code to generate tf-serving compatable model after the training progress. The wide\_deep.py code is modified from https://github.com/tensorflow/models/blob/master/official/wide_deep/wide_deep.py. We need to define the input processing func (e.g., serving\_input\_receiver\_fn) and add one line at the end of main() func to export the model:

    # used by serving_input_receiver_fn()
    def parse_csv(value):
    columns = tf.decode_csv(value, record_defaults=_CSV_COLUMN_DEFAULTS)
    features = dict(zip(_CSV_COLUMNS, columns))
    return features

    # the serving input processing func
    def serving_input_receiver_fn():
    """An input receiver that expects a serialized tf.Example."""
    receiver_tensors = tf.placeholder(dtype=tf.string,
                                           shape=[None,],
                                           name='input_example_tensor')
    features = parse_csv(receiver_tensors)
    return tf.estimator.export.ServingInputReceiver(features, receiver_tensors)

    def main(unused_argv):
    	...
    
    	# Save model to create inference.
    	model.export_savedmodel(FLAGS.serving_checkpoint, serving_input_receiver_fn)
    
Thanks to the estimator interface, the estimator object can directly export tf-serving compatable model through export_savedmodel if we provide the serving\_input\_receiver\_fn func. The serving\_input\_receiver\_fn func defines two variables: 1) the *features* argument for ServingInputReceiver is the data that will be feed to the estimator.model\_fn(); the *receiver\_tensor* is the actual input from inference call. For more details, please refer to https://www.tensorflow.org/programmers_guide/saved_model.

### Generate Wide&Deep tf-serving model
Run the following code to generate the wide&deep model, for more details please refer to https://github.com/tensorflow/models/tree/master/official/wide_deep

    python wide_deep.py --train_data /PATH_TO/census_data/adult.data --test_data /PATH_TO/census_data/adult.test
    
Note: To generate the tf-serving model, please use the wide\_deep.py code provided by us. We have made the necessary modifications!!! The output will be in /tmp/census\_data/

## Build Wide&Deep Inference Service with UAI Inference toolkit
Building a Wide&Deep inference service docker need some preparations:

1. Write a simple Inference class to load the model, process the data, and run the inference logic.
2. Provide a config file to tell UAI Inference system where to load the model
3. Get the basic UAI Inference docker base image

For more details please refer to https://docs.ucloud.cn/ai/uai-inference/index

### Writing Service Code
We provide the example service code in inference.py. We defined WideDeepModel which derived from TFServingAiUcloudModel. TFServingAiUcloudModel has implemented the generic logic of loading tf-serving capable model as well as the logic of doing the inference (with a default feature of autobatching).

In WideDeepModel we only need to implement one funcs:

1. execute(self, data, batch_size) which will do the inference. We only need to call the TFServingAiUcloudModel.execute func to process the input 'data' array and get the result list: output_tensor. And the we format the output into string arrays. (You can format it into json also)

### Define the Config File
We need to provide the config file to tell the UAI Inference system to get the basic information to load the tf-serving capable model. The config file should include following info:

1. "exec" tells which file is used as the entry-point of the user-defined inference logic and which main class is used. 
2. "tensorflow" tells which model related info should be parsed by UAI Inference system.

The config file in this example is as follow:

    "http_server" : {
        "exec" : {
            "main_class": "WideDeepModel",
            "main_file": "inference"
        },
        "tensorflow" : {
            "model_dir" : "./checkpoint_dir/",
            "tag": ["serve"],
            "signature": "predict",
            "input": {
                "name": "input"
            },
            "output": {
                "name": ["classes", "logits"]
            }
        }
    }
    
The entry-point file module is inference (Note we must omit the .py suffix). The user-defined inference main class is WideDeepModel.

It provides several info for the system to load the model. These infos are necessary to load a tf-serving capable module which is usually a protobuf file e.g. checkpoint\_dir/saved\_model.pb：

1. model\_dir: tell where to find the model file
2. tag: tell which graph to load from the model file, it should be "serve" here as compatable with tf.saved\_model.tag\_constants.SERVING. (For more details please see: https://github.com/tensorflow/tensorflow/blob/master/tensorflow/python/saved_model/tag_constants.py)
3. signature: use the predefined 'predict' API in Estimator
4. input: tell the input tensor name
5. output: tell the output tensor name, both *classes* and *logits* are predefined by the Estimator.

Note: get get the exact input/output tensor name, you should use the saved\_model\_cli to generate them. Please refer to https://www.tensorflow.org/programmers_guide/saved_model for more details.

### Build the docker image
We build the wide&deep inference service docker image based on UCloud AI Inference Docker base image: uhub.service.ucloud.cn/uaishare/cpu_uaiservice\_ubuntu-14.04\_python-2.7.6\_tensorflow-1.4.0:v1.1, you can get it by:

    # In UCloud VM
    sudo docker pull uhub.service.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-14.04_python-2.7.6_tensorflow-1.4.0:v1.1
    
    # Internet
    sudo docker pull uhub.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-14.04_python-2.7.6_tensorflow-1.4.0:v1.1
    
#### Preparing code and model
We have provide the example inference code (wide\_deep/inference.py) and the config file conf.json. You should put them together into wide\_deep/ directory. We also provide the wide&deep model into checkpoint\_dir:

    # ls
    wide\_deep
    # ls wide\_deep
    checkpoint_dir conf.json inference.py

#### Preparing dockerfile
We provide the example dockerfile to pack the inference service docker image. You should put it into the same directory with the wide\_deep package.

	# ls
	wide\_deep/ uaiservice.Dockerfile
	
The dockerfile(uaiservice.Dockerfile) include following contents:

    FROM  uhub.service.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-14.04_python-2.7.6_tensorflow-1.4.0:v1.1

    EXPOSE 8080
    ADD ./wide\_deep /ai-ucloud-client-django/
    ADD ./wide\_deep/conf.json  /ai-ucloud-client-django/conf.json
    ENV UAI_SERVICE_CONFIG /ai-ucloud-client-django/conf.json
    CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi

1. build the docker image based on UCloud AI Inference Docker base image. (Note if you are using UCloud VM you can use 'uhub.service.ucloud.cn' otherwise you should change it into 'uhub.ucloud.cn'
2. EXPOSE 8080 port for http service
3. ADD all code under wide\_deep into /ai-ucloud-client-django/. (Note the root path when the django server start is /ai-ucloud-client-django/)
4. ADD the conf.json into /ai-ucloud-client-django/, The django server will automatically load a json config file to get all running info. For more details of how json file is organized please refer: [Define the Config File](###define-the-config-file)
5. Set the UAI_SERVICE_CONFIG environment to tell django server to load the config file named 'conf.json'
6. use gunicorn to run the server

#### Build your own service docker
With the above docker file we can now build our own service docker image:

    sudo docker build -t wd-serve:test -f uaiservice.Dockerfile .

#### Run and Test
We can run the server directly:

    sudo docker run -it -p 8080:8080 wd-serve:test
    
Then we can test it by:

     curl -X POST http://127.0.0.1:8080/service -d "58,?,299831,HS-grad,9,Married-civ-spouse,?,Husband,White,Male,0,0,35,United-States,<=50K"

### Deploy to UAI Inference Platform
Please refer to https://docs.ucloud.cn/ai/uai-inference/index for more details
