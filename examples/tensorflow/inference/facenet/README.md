# Face Detection Example with FaceNet
This example shows how to use FaceNet to do face recognition inference. Here we shows how to build a face recognition inference service based on UAI Inference system. We assume you have already known how to train a FaceNet model (https://github.com/davidsandberg/facenet). 

## Intro
UAI Inference platform can serve inference services through HTTP requests. We provide the basic docker image containing a django server which can load the user-defined inference module to do the service. To implement a inference module, you only need to implement two funcs: load\_model and execute. For more details please refer to https://docs.ucloud.cn/ai/uai-inference/guide/principle.

In this example, we provide two inference service examples:

1. FaceCompareModel: Accept two 'face' images and calculate the distance of these two faces.
2. FaceEmbedModel: Accept one 'face' image and calculate its embedding using FaceNet Model.

### Setup
You should download the current directory into your work place. You should also train a FaceNet model or download one from https://github.com/davidsandberg/facenet, and put it under the code dir.

We put all these files into one directory:

	/data/facenet/inference/
	|_ code
	|  |  align
	|  |  |_ det1.npy
	|  |  |_ det2.npy
	|  |  |_ det3.npy
	|  |  |_ detect_face.py
	|  |_ facenet.py
	|  |_ facenet_inference.py
	|  |_ gen_example_json.py
	|  |_ gen_img_json.py
	|  |_ checkpoint_dir
	|  |  |_ 20180402-114759.pb
	|  |  |_ model-20180402-114759.ckpt-275.data-00000-of-00001
	|  |  |_ model-20180402-114759.ckpt-275.index  
	|  |  |_ model-20180402-114759.meta
	|_ facenet-compare-cpu.Dockerfile
	|_ facenet-compare.conf
	|_ facenet-embed-cpu.Dockerfile
	|_ facenet-embed.conf

### UAI Inference Example
We provide facenet\_inference.py which implements both FaceCompareModel and FaceEmbedModel. Here, we take FaceCompareModel as an example. The implementation of FaceEmbedModel is similar.

For FaceCompareModel, it implements two funcs:

1. load\_model(self), which loads the FaceNet model from checkpoint\_dir. 

2. execute(self, data, batch_size), which handles the inference requests. The django server will invoke FaceCompareModel->execute when it receive requests. It will process the input 'data' array one by and by invoking self.compare(data[i]) to calculate the distance of the face pair and generate the result list. We format each distance float into string object. (You can format it into json also)

#### Define the Config File
We need to provide the config file to tell the UAI Inference system to get the basic information to load the FaceCompareModel/FaceEmbedModel and the FaceNet model. The config file should include following info:

1. "exec" tells which file is used as the entry-point of the user-defined inference logic and which main class is used. 
2. "tensorflow" tells which model related info should be parsed by UAI Inference system.

You can find the example config file of: facenet-compare.conf and facenet-embed.conf

#### Packing Inference Docker
We provide facenet-compare-cpu.Dockerfile and facenet-embed-cpu.Dockerfile for you to build the local inference docker image. Take facenet-compare-cpu.Dockerfile as an example:

	FROM uhub.service.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-16.04_python-2.7.6_tensorflow-1.6.0:v1.0

	EXPOSE 8080
	ADD ./code/ /ai-ucloud-client-django/
	ADD ./facenet-compare.conf  /ai-ucloud-client-django/conf.json
	ENV UAI_SERVICE_CONFIG /ai-ucloud-client-django/conf.json
	CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi

1. build the docker image based on UCloud AI Inference Docker base image. (Note if you are using UCloud VM you can use 'uhub.service.ucloud.cn' otherwise you should change it into 'uhub.ucloud.cn'
2. EXPOSE 8080 port for http service
3. ADD all code under ./code into /ai-ucloud-client-django/. (Note the root path when the django server start is /ai-ucloud-client-django/)
4. ADD the conf.json into /ai-ucloud-client-django/, The django server will automatically load a json config file to get all running info. For more details of how json file is organized please refer: [Define the Config File](#define-the-config-file)
5. Set the UAI_SERVICE_CONFIG environment to tell django server to load the config file named 'conf.json'
6. use gunicorn to run the server

#### Build Your Own Inference Docker
With the above docker file we can now build your own inference docker image(Your directory should looks like [Setup](#setup)):

    sudo docker build -t face-compare:test -f facenet-compare-cpu.Dockerfile .

    sudo docker build -t face-embed:test -f facenet-embed-cpu.Dockerfile .

#### Run FaceNet Inference Service Locally
We can run the face-compare server as

    sudo docker run -it -p 8080:8080 face-compare:test

You can run the face-embed server as 

    sudo docker run -it -p 8080:8080 face-embed:test

### Test FaceNet Inference Service Locally
Both FaceCompareModel and FaceEmbedModel take json obj as input. The format looks like this:

	{
		'cnt': cnt, 
		'images': [image1, image2],
	}

#### Generate Json Request Data
We provide two tools to generate json input:

1. gen\_example\_json.py: It takes a list of images of 'face' as input and output a json file 'test.json'. (Note the 'face' image should be aligned through MTCNN)

	$ cd code
	$ python gen_example_json.py --image_files A.jpeg B.jpeg

2. gen\_img\_json.py: It takes a list of images as input and output a json file 'test.json'. It will automatically use MTCNN to do face alignment.

    $ cd code
    $ python gen_img_json.py --image_files A.jpeg B.jpeg

#### Test FaceNet Inference Service Locally
You should generate your test.json fisrt. Then you can start the service and test it.

1. For face-compare:

	$ cd code
	$ python gen_img_json.py --image_files A.jpeg B.jpeg

	$ sudo docker run -it -p 8080:8080 face-compare:test

	$ curl -X POST http://127.0.0.1:8080/service -T test.json

2. For face-embed:

	$ cd code
	$ python gen_img_json.py --image_files A.jpeg

	$ sudo docker run -it -p 8080:8080 face-embed:test

	$ curl -X POST http://127.0.0.1:8080/service -T test.json

### Deploy FaceNet Inference Service into UAI Inference Platform
Please refer to https://docs.ucloud.cn/ai/uai-inference/index for more details. You can directly use the docker image build in [Build](#build-your-own-inference-docker)