# Face-compare Case
This example shows how to use MTCNN and FaceNet to do face-compare application. 

## Intro
UAI Inference platform provides inference services through HTTP requests. We provide the basic docker images containing django servers which load user-defined inference modules to perform the service. To implement an inference module, you need to implement two methods for the model class: <inference_model>.load\_model() and <inference_model>.execute(). For more details please refer to: 
https://docs.ucloud.cn/ai/uai-inference/guide/principle

In this example, we shows how to build a face-compare application by using MTCNN and FaceNet based on UAI Inference framework. The whole face-compare progress work as follows:

	Input -> face-service -> facenet-mtcnn
     	                  -> facenet-compare

1. The Input is a json object containing two Face-PIC. (use gen_example_json.py to transfer 2 PIC files into one json object)
2. Call face-service to do the distance compare of two faces (from Input)
3. face-service will call facenet-mtcnn first to detect face in the both PICs
4. face-service will call facenet-compare to calculate the distance of two faces

All PICs are packed into json object during transferring between face-service, facenet-mtcnn and facenet-compare. We provide uai.contrib.image.img_utils.py to encode/decode PIL.Image objects into json object.

## Preparation
You should prepare both MTCNN and FaceNet. You can refer to examples/tensorflow/inference/facenet#Setup to get basic code of MTCNN and FaceNet. You can download the current directory into your work place. And then put MTCNN and FaceNet related files (including codes and modes) in the the same work place. 

We put all these files into one directory:

	/data/face-compare
	|_ code
	|  |_ align
	|  |  |_ det1.npy
	|  |  |_ det2.npy
	|  |  |_ det3.npy
	|  |  |_ detect_face.py
	|  |_ facenet.py
	|  |_ facecompare_service.py
	|  |_ facenet_json_inference.py
	|  |_ gen_example_json.py
	|  |_ checkpoint_dir
	|  |  |_ 20180402-114759.pb
	|  |  |_ model-20180402-114759.ckpt-275.data-00000-of-00001
	|  |  |_ model-20180402-114759.ckpt-275.index  
	|  |  |_ model-20180402-114759.meta
	|_ face-service.Dockerfile
	|_ face-service.conf
	|_ facenet-compare-json-cpu.Dockerfile
	|_ facenet-compare-json.conf
	|_ facenet-mtcnn-json-cpu.Dockerfile
	|_ facenet-mtcnn-json.conf

## Build Your Own Inference Docker
You can use the dockerfile provided here to build your own inference docker image:

    sudo docker build -t face-service:test -f facenet-service.Dockerfile .

    sudo docker build -t face-mtcnn:test -f facenet-mtcnn-json-cpu.Dockerfile .

    sudo docker build -t face-compare:test -f facenet-compare-json-cpu.Dockerfile .

Note: Please pay attention to face-service.conf, it contains backend.mtcnn and backend.compare keywords to tell face-service server which mtcnn server and facenet-compare server located. By default it use localhost:

    "backend" : {
        "mtcnn" : "http://localhost:8081/service",
        "compare" : "http://localhost:8082/service"
    }

Note: you should reinstall the uai-sdk into docker (facenet-service.Dockerfile, facenet-mtcnn-json-cpu.Dockerfile and facenet-compare-json-cpu.Dockerfile provided has already add this step) as the official caffe-docker provied by UCloud does not include uai.contrib lib now.

## Run the service
You can run the service as follows:

	sudo docker run --net host -p 8080:8080 face-service:test
	sudo docker run -p 8081:8080 face-mtcnn:test
	sudo docker run -p 8082:8080 face-compare:test

Now we can use following cmd to do a facecompare:

    #gen_example_json.py will generate a test.json file
    python gen_example_json.py --image_files img1 img2
    curl -X POST http://localhost:8080/service -T test.json