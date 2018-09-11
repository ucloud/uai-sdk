# Object-detection Example
Object-detection example shows how to run TensorFlow object detection training on UAI Train Platform. The example is based on https://github.com/tensorflow/models/tree/master/research/object_detection

# Setup
You should prepare your own training data and pretrained model before running the task. As UAI Train nodes does not provide Internet access, you should prepare your data locally.

## Intro
The object detection example directly use the code in https://github.com/tensorflow/models/tree/master/research/object_detection. As it depends on the slim package and object_detection package under tensorflow/models/research/, we provide the Dockerfile to show how to pack these python packages into the docker.

## UAI Example
We made the following modifications to run the object-detection retraining on UAI Train Platform:

1. Provide a Dockerfile named uaitrain.Dockerfile for building the docker
2. Provide the modified faster_rcnn_resnet101_pets.config

We use the pet detection as the example. Clone the tensorflow model module to your local machine:

	git clone https://github.com/tensorflow/models.git

The detailed info can be found in https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/running_pets.md

### Preparing the Data
Please follow:
https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/running_pets.md to download the training data and the pre-trained model: faster_rcnn_resnet101. 
The example use the resnet101 model and the Oxford-IIIT Pets Dataset:
http://www.robots.ox.ac.uk/%7Evgg/data/pets/
Acquire a copy of category dictionary from:
https://github.com/tensorflow/models/blob/master/research/object_detection/data/pet_label_map.pbtxt
name it as label_map.pbtxt and put it in the same root directory where the pet images and annotations are unzipped.

#### Prepare self-sourced dataset
In case you intend to use your own image dataset, you should prepare several sets of data as input. For each image used, a copy of the the following is required with the same prifix, e.g.: Abyssinian_01.jpg and Abyssinian_01.xml. Image name should be in the form of ${image_content}\_${content_index}.{jpg/png}, e.g.: Abyssinian_01.jpg or Teacup_1100.png.
1. Image in the form of jpeg or png containing exactly one object expected to be detected;
2. An .xml file containing the ground truth of where the object/objects should be detected, with information of:
    image name;
    image size(height, width);
    object coordinate(xmin, xmax, ymin, ymax).
Refer to the provided pet dataset example for how an xml file looks like.

A copy of index-category dictionary is needed with the name label_map.pbtxt. It indicates the object-categories and index used in training:
    
    item {
        id: 1
        name: 'Abyssinian'
    }
    item {
        id: 2
        name: 'basset_hound'
    }
    
The list must include all possible categories of objects that are in the dataset. 
A list of data used for training is needed with the name trainval.txt recording all the image file's prefixes that you would like to use in training:
    Abyssinian_01
    basset_hound_02
    teacup_1100
The dataset listed will be later randomly shuffled and divided with 70% data used in training and 30% used in training-evaluation (but not inference). 
Put all the files under the same directory as:

    /data/object-detect-prep/
	|_ label_map.pbtxt
	|_ annotations
	|  |_ trainval.txt
	|  |_ xmls
	|  |  |_ Abyssinian_1.xml
	|  |  |_ basset_hound_2.xml
	|  |  |_ Teacup_1100.xml
	|_ images
	|  |_ Abyssinian_1.jpg
	|  |_ basset_hound_2.jpg
	|  |_ Teacup_1100.png


#### Create Local Test Data Path
Download the dataset and use the object\_detection/dataset\_tools/create\_pet\_tf\_record.py to generate the tfrecords. These record files are information and data of the training images.

We put all the tfrecord, the pet\_label\_map.pbtxt from object\_detection/data/ as well as the resnet101 ckpt into /data/object-detect/data/.
Note that the tf record file type could be changed in future version of tensorflow examples. Here lies the version of file names and types for the April 30, 2018 release of Models/Research/Object-detect module.

    # cd /data/object-detect/data/
    # ls
    model.ckpt.data-00000-of-00001  model.ckpt.index  model.ckpt.meta  label_map.pbtxt
    obj_train.record-00000-of-00010  obj_train.record-00001-of-00010  obj_train.record-00002-of-00010
    obj_train.record-00003-of-00010  obj_train.record-00004-of-00010  obj_train.record-00005-of-00010
    obj_train.record-00006-of-00010  obj_train.record-00007-of-00010  obj_train.record-00008-of-00010
    obj_train.record-00009-of-00010
    obj_val.record-00000-of-00010  obj_val.record-00001-of-00010  obj_val.record-00002-of-00010
    obj_val.record-00003-of-00010  obj_val.record-00004-of-00010  obj_val.record-00005-of-00010
    obj_val.record-00006-of-00010  obj_val.record-00007-of-00010  obj_val.record-00008-of-00010
    obj_val.record-00009-of-00010

#### Preparing the running config
We also put the modified faster\_rcnn\_resnet101.config into /data/object-detect/data/. The modifications include:

    Line 106:
      fine_tune_checkpoint: "/data/data/model.ckpt"
      
    Line 121:
        input_path: "/data/data/obj_train.record*"
      }
      label_map_path: "/data/data/label_map.pbtxt"
    
    Line 135:
        input_path: "/data/data/obj_val.record*"
      }
      label_map_path: "/data/data/label_map.pbtxt"
      
All the modifications are necessary to running the train job on UAI Train Platform. The UAI Train Platform will automatically put the data into /data/data/ path. We have provided the modified faster\_rcnn\_resnet101.config in:
uai-sdk/examples/tensorflow/train/object-detection/samples/
If you are using self-sourced dataset, change the config file to adjust the category count:

    Line 9: num_classes: ${your_category_count}

You can also change the training step counts by setting:

    Line 112: num_steps: ${your_step_count}
    
Whereas default is 200,000 steps. For a short training test period, 20 steps is sufficient.

Note that the "/data/data/pet_faces_val.record*" matches the file name and format discussed in Create Local Test Data Path. If the files generated to be tf record are modified in later version of Tensorflow, change the config file accordingly so it matches all the files generated, or kindly refer to the config file offered within the Tensorflow project:
https://github.com/tensorflow/models/blob/master/research/object_detection/samples/configs/faster_rcnn_resnet101_pets.config

Now the /data/object-detect/data/ include following files:

    # cd /data/object-detect/data/
    # ls
    faster_rcnn_resnet101.config  model.ckpt.data-00000-of-00001  model.ckpt.index  model.ckpt.meta  label_map.pbtxt
    obj_train.record-00000-of-00010  obj_train.record-00001-of-00010  obj_train.record-00002-of-00010
    obj_train.record-00003-of-00010  obj_train.record-00004-of-00010  obj_train.record-00005-of-00010
    obj_train.record-00006-of-00010  obj_train.record-00007-of-00010  obj_train.record-00008-of-00010
    obj_train.record-00009-of-00010
    obj_val.record-00000-of-00010  obj_val.record-00001-of-00010  obj_val.record-00002-of-00010
    obj_val.record-00003-of-00010  obj_val.record-00004-of-00010  obj_val.record-00005-of-00010
    obj_val.record-00006-of-00010  obj_val.record-00007-of-00010  obj_val.record-00008-of-00010
    obj_val.record-00009-of-00010

These are all the data required for training.

### Build the Docker images

UCloud provides a pre-built docker image for training: objdetect-train-gpu-tf16. You can use the following code to pull it:

	sudo docker pull uhub.ucloud.cn/uai_demo/tf-objdetect-train-gpu-tf16:latest

Or you can do the following to build on your own. We provide the basic Dockerfile to build the docker image for training object-detection model written as:

    From uhub.ucloud.cn/uaishare/gpu_uaitrain_ubuntu-16.04_python-2.7.6_tensorflow-1.6.0:v1.0

    RUN apt-get update
    RUN apt-get install python-tk -y

    ADD ./research /data/

    RUN cd /data/ && python setup.py install && cd slim && python setup.py install


We should run the docker build under PATH\_TO/tensorflow/models/. To build the docker image, the following steps are performed by the above dockerfile commands:

1. Use uaitrain tf1.6 version as the base image of the whole docker image.
2. Update apt-get and install python-tk lib.
3. Copy all the files under research/ into /data/
4. Install the object-detection lib and the slim lib from tensorflow/models/research.

We can run the following cmd to build the image:

    cd PATH_TO/tensorflow/models
    cp PATH_TO/uaitrain.Dockerfile ./
    sudo docker build -f uaitrain.Dockerfile -t uhub.ucloud.cn/<YOUR_UHUB_REGISTRY>/tf-objdetect:uaitrain .

These commands switches to the tensorflow/models directory, copy the dockerfile here and build the docker with the above commands in the Dockerfile. You can use tag the docker with any docker-name here if you want by changing the suffix after <UHUB_REGISTRY>/, so you can manage multiple versions of dockers without confusion. After building the image, we get a docker image named uhub.ucloud.cn/<YOUR_UHUB_REGISTRY>/tf-objdetect:uaitrain, which is the same as the docker provided.

### Run the train
We can simply use the following cmd to run the local test(GPU version). Make sure you have a GPU and relevant environment to run it on. Note that if you use any other data storage directory other than "/data/object-detect/data", you should change the same path in the command accordingly, for the parameter:
	
	-v /data/object-detect/data/:/data/data
	
replaces the directories, so that when the program goes to "/data/data/", it actually redirects into "/data/object-detect/data/" for the images and xmls. Here is the default command:

    sudo nvidia-docker run -it -v /data/object-detect/data/:/data/data -v /data/object-detect/output:/data/output uhub.service.ucloud.cn/uai_dockers/tf-objdetect:uaitrain /bin/bash -c "cd /data && /usr/bin/python /data/object_detection/train.py --pipeline_config_path=/data/data/faster_rcnn_resnet101.config --train_dir=/data/output"
    
Note: we use use --pipeline\_config\_path=/data/data/faster\_rcnn\_resnet101.config to tell the train.py script to use the training config under /data/data/ (as stated before, it is actually in /data/object-detect/data, or wherever you change it to) and use --train\_dir=/data/output to tell the training script to output the model into /data/output. (When you are running the train job in UAI Train Platform, we will automatically put data into /data/data before job start and upload data inside /data/output after job finished.)

Here is the command to start the training if it is performed on UAI-Training Platform:

	/data/object_detection/train.py --pipeline_config_path=/data/data/faster_rcnn_resnet101.config --train_dir=/data/output

Note here that some directory replacement parameters are left out because UAI-Train platform forcingly applies the replacement (to /data/data/ and /data/output/ respectly, so do not use these 2 directories to store data because they will not be found). Let the input path be /data/object-detect/data/, or wherever you put data, and output path be /data/object-detect/output/.


### Results
UAI Training produces the trained model containing in several files: some_model.data-00000-of-00001, some_model.meta, some_model.index and checkpoint. For the object detection inference example: 
https://github.com/ucloud/uai-sdk/edit/master/examples/tensorflow/inference/object-detect/
A model in the from of frozen_inference_graph.pb is required. Refer to: 
https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/exporting_models.md
for exporting such a model file.


### Docker Image
We have provided the pre-build docker image based on TensorFlow-1.4, you can get the docker image by:

    # Through UCloud Internal Network
    docker pull uhub.service.ucloud.cn/uaishare/tf-obj-detect:tf-1.4

    # Through Internel Network
    docker pull uhub.ucloud.cn/uaishare/tf-obj-detect:tf-1.4
