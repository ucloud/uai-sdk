# Object-detection Example
Object-detection example shows how to run TensorFlow object detection training on UAI Train Platform. The example is based on https://github.com/tensorflow/models/tree/master/research/object_detection

# Setup
You should prepare your own training data and pretrained model before running the task. As UAI Train nodes does not provide network access, you should prepare your data locally.

## Intro
The object detection example directly use the code in https://github.com/tensorflow/models/tree/master/research/object_detection. As it depends on the slim package and object\_detection package under tensorflow/models/research/, we provide the Dockerfile to show how to pack these python packages into the docker.

## UAI Example
We made the following modifications to run the object-detection retraining on UAI Train Platform:

1. Provide a Dockerfile named uaitrain.Dockerfile for building the docker
2. Provide the modified faster\_rcnn\_resnet101\_pets.config

We use the pet detection as the example. The detailed info can be found in https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/running_pets.md

### Preparing the Data
Please follow the research/object\_detection/g3doc/running\_pets.md to download the training data and the pretrained model. The example use the resnet101 model and the Oxford-IIIT Pets Dataset.

#### Create Local Test Data Path
Suppose you have downloaded the dataset and use the object\_detection/dataset\_tools/create\_pet\_tf\_record.py to generate the tfrecords. We put all the tfrecord, the pet\_label\_map.pbtxt from object\_detection/data/ as well as the resnet101 ckpt into /data/object-detect/data/. 

    # cd /data/object-detect/data/
    # ls
    model.ckpt.data-00000-of-00001  model.ckpt.index  model.ckpt.meta  pet_label_map.pbtxt  pet_train_with_masks.record  pet_val_with_masks.record

#### Preparing the running config
We also put the modified faster\_rcnn\_resnet101\_pets.config into /data/object-detect/data/. The modifications includes:

    Line 110:
      fine_tune_checkpoint: "/data/data/model.ckpt"
      
    Line 125:
        input_path: "/data/data/pet_train_with_masks.record"
      }
      label_map_path: "/data/data/pet_label_map.pbtxt"
    
    Line 139:
        input_path: "/data/data/pet_val_with_masks.record"
      }
      label_map_path: "/data/data/pet_label_map.pbtxt"
      
All the modifications are necessary to running the train job on UAI Train Platform. The UAI Train Platform will automatically put the data into /data/data/ path. We have provided the modified faster\_rcnn\_resnet101\_pets.config in uai-sdk/examples/tensorflow/train/object-detection/samples/

Now the /data/object-detect/data/ include following files:

    # ls
    faster_rcnn_resnet101_pets.config  model.ckpt.data-00000-of-00001  model.ckpt.index  model.ckpt.meta  pet_label_map.pbtxt  pet_train_with_masks.record  pet_val_with_masks.record

### Build the Docker images
We provide the basic Dockerfile to build the docker image for training object-detection model:

    From uhub.service.ucloud.cn/uaishare/gpu_uaitrain_ubuntu-14.04_python-2.7.6_tensorflow-1.4.0:v1.0

    RUN apt-get update 
    RUN apt-get install python-tk -y

    ADD ./research /data/

    RUN cd /data/ && python setup.py install && cd slim && python setup.py install

We should run the docker build under PATH\_TO/tensorflow/models/. To build the docker image, we do the following steps:

1. Install python-tk lib
2. Copy all the files under research/ into /data/
3. Install the object-detection lib and the slim lib

We can run the following cmd to build the image:

    # cd PATH_TO/tensorflow/models
    # cp PATH_TO/uaitrain.Dockerfile ./
    # sudo docker build -f uaitrain.Dockerfile -t uhub.ucloud.cn/<YOUR_UHUB_REGISTRY>/tf-objdetect:uaitrain .
    
You can use any docker-name here if you want. After build the image, we get a docker image named uhub.ucloud.cn/<YOUR_UHUB_REGISTRY>/tf-objdetect:uaitrain.

### Run the train
We can simply use the following cmd to run the local test.(GPU version)

    sudo nvidia-docker run -it -v /data/object-detect/data/:/data/data -v /data/object-detect/output:/data/output uhub.service.ucloud.cn/uai_dockers/tf-objdetect:uaitrain /bin/bash -c "cd /data && /usr/bin/python /data/object_detection/train.py --pipeline_config_path=/data/data/faster_rcnn_resnet101_pets.config --train_dir=/data/output"
    
Note: we use use --pipeline\_config\_path=/data/data/faster\_rcnn\_resnet101\_pets.config to tell the train.py script to use the training config under /data/data/ and use --train\_dir=/data/output to tell the training script to output the model into /data/output. (When you are running the train job in UAI Train Platform, we will automatically put data into /data/data before job start and upload data inside /data/output after job finished.)
