# Not Suitable For Work Probability Deduction
This example shows how to deduce an image's probability to be not suitable for work (in the aspect of sexual-content related). Here we show how to build an nsfw probability inference service based on uai-sdk Inference docker and structure. A trained model is given, while you can apply other caffe models as well.

## Origin
The image pre-process, algorithm, model and original codes are redistributed from another GitHub project in the from of source codes and the codes are modified to adapt to uai-sdk images and structures. Please visit
	https://github.com/yahoo/open_nsfw
for original source. The copyright information is given as below:

Copyright 2016, Yahoo Inc.

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


## Intro
UAI Inference platform provides inference services through HTTP requests. We provide the basic docker images containing django servers which load user-defined inference modules to perform the service. To implement an inference module, you need to implement two methods for the model class: <inference_model>.load\_model() and <inference_model>.execute(). For more details please refer to: 
https://docs.ucloud.cn/ai/uai-inference/guide/principle

In this example, we provide the inference service example, NsfwModel, which accept one image and returns the probability of it being improper for workplace and workhours (in the aspect of sexual-content related).

## Setup
Download the current directory into your workplace. A model is given in:
https://github.com/yahoo/open_nsfw/tree/master/nsfw_model. Copy the two files to directory checkpoint_dir/ under code/, and rename them to the same name (for the example below: resnet.caffemodel and resnet.prototxt). You may use any other caffe model with the same procedure.

Put all these files into one directory:

	/data/nsfw/
	|_ code
	|  |_ checkpoint_dir
	|  |  |_ resnet.caffemodel
	|  |  |_ resnet.prototxt
	|  |_ nsfw_inference.py
	|_ nsfw-cpu.Dockerfile
	|_ caffe_nsfw.conf

## UAI Inference Example
Class NsfwModel is implemented within nsfw_inference.py. The class overrides 2 methods:
1. load\_model(self), which loads the NSFW model discussed above. 

2. execute(self, data, batch_size), which handles the inference requests. The django server calls NsfwModel->execute when it receives requests. The method then pre-processes the list of images from input, calculates the probability of each of them, and returns a list of probabilities. Eventually, the server returns the list of probabilities to the request sender as a string.

### Alter the Config File
We need to provide a config file to maintain the service configures. The config file includes the following info:

1. "exec": infers the file used as the entry-point and the class used within the file.
2. "caffe": infers the directory containing the model files, and the name of the model files. The name is "resnet" by default. You can use another model by changing it to your model's name. Please refer to Setup section to see where to put the model files.

{
    "http_server" : {
        "exec" : {
            "main_class": "NsfwModel",
            "main_file": "nsfw_inference"
        },
        "caffe" : {
            "model_dir" : "./checkpoint_dir",
            "model_name" : "resnet"
        }
    }
}

You can find the example config file: caffe_nsfw.conf

### Packing Inference Docker
We provide nsfw-cpu.Dockerfile to build the inference docker image.

	FROM uhub.service.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-14.04_python-2.7.6_caffe-1.0.0:v1.2

	EXPOSE 8080
	ADD ./code/ /ai-ucloud-client-django/
	ADD ./caffe_nsfw.conf  /ai-ucloud-client-django/conf.json
	ENV UAI_SERVICE_CONFIG "/ai-ucloud-client-django/conf.json"

	CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi


1. build the docker image based on UCloud AI Inference Docker base image. (Note if you are using UCloud VM you can use 'uhub.service.ucloud.cn' otherwise you should change it into 'uhub.ucloud.cn')
2. EXPOSE 8080 port for http service
3. ADD all code under ./code to /ai-ucloud-client-django/. (Note the root path when the django server start is /ai-ucloud-client-django/)
4. ADD the config file to /ai-ucloud-client-django/, The django server will automatically load a json config file to get all running info. For more details of how json file is organized please refer: [Alter the Config File](#Alter-the-config-file)
5. Set the UAI_SERVICE_CONFIG environment to tell django server to load the config file named 'conf.json'
6. use gunicorn to run the server

### Build Your Own Inference Docker
With the above docker file we can now build your own inference docker image(Your directory should looks like [Setup](#setup)):

    sudo docker build -t caffe-nsfw-cpu:test -f nsfw-cpu.Dockerfile .

### Run MTCNN Inference Service Locally
We can run the mtcnn server as

    sudo docker run -it -p 8080:8080 caffe-nsfw-cpu:test
    
    
### Test MTCNN Inference Service Locally
MTCNNCpuModel takes image obj as input (png or jpeg)

	$ curl -X POST http://127.0.0.1:8080/service -T naked_elephant.jpg

**Note: We set http request timeout to 10 seconds in the gunicorn. You can change it by modify /ai-ucloud-client-django/gunicorn.conf.py (inside docker img) to change the timeout setting.**

## Deploy NSFW Inference Service onto UAI Inference Platform
Please refer to https://docs.ucloud.cn/ai/uai-inference/index for more details. You can directly use the docker image build in [Build](#build-your-own-inference-docker)
