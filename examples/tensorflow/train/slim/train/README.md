# TF Slim Example
TF-slim is a new lightweight high-level API of TensorFlow (tensorflow.contrib.slim) for defining, training and evaluating complex models. 

Here we shows how to classify our pictures data with TF-slim example code on UAI Platform. This example is based on [tensorflow-slim](https://github.com/tensorflow/models/tree/master/research/slim).
You can directly use the code from [tensorflow-slim](https://github.com/tensorflow/models/tree/master/research/slim) with some appropriate modifications.

We have provided the modified code for you. You can find it under examples/tensorflow/train/slim/train/

Chinese version of the case introduction you can refer to https://cms.docs.ucloudadmin.com/ai/uai-train/case/slim/intro.


## Data prepare

In this example, we use FER2013 dataset to train Facial expression recognition model.
The FER2013 dataset is a facial expression recognition dataset. 
There are seven categories in the dataset, namely angry, disgust, fear, happy, neutral, sad, and surprise. 
There are 35,886 images in the dataset, each of which is 48 x 48 x 1. 

The storage structure of the FER2013 data set is as follows:

```
|_ fer/pic/
  |_ angry\
     |_ 00000_1.jpg
     |_ ...
  |_ disgust\
  |_ fear\
  |_ happy\
  |_ neutral\
  |_ sad\
  |_ surprise\
```

## Packing TF-Slim code
After Preparing the code (by replace the train_image_classifier.py、download_and_convert_data.py and code in deployment\ and datasets\), 
you can pack the tf-slim docker. 

We provide the slim.Dockerfile:

    FROM uhub.service.ucloud.cn/uaishare/gpu_uaitrain_ubuntu-16.04_python-2.7.6_tensorflow-1.5_models:v1.8.0

    COPY ./slim/ /data/

It use the base image provided by UAI (tensorflow 1.5 with tf-models 1.8.0) and copy the code into /data/.

Suppose you get the slim code, you can do the following steps to build your own UAI slim image:

    $ cd ${SLIM_CODE_DIR}
    $ ls slim/
    BUILD datasets/ deployment/ ... train_image_classifier.py WORKSPACE
    $ cp ${UAI-SLIM_EXAMPLE}/slim.Dockerfile .
    $ cp ${UAI-SLIM_EXAMPLE}/train_image_classifier.py ./slim/
	$ cp ${UAI-SLIM_EXAMPLE}/download_and_convert_data.py ./slim/
	$ cp -r ${UAI-SLIM_EXAMPLE}/datasets/. ./slim/datasets/
	$ cp ${UAI-SLIM_EXAMPLE}/deployment/model_deploy.py  ./slim/deployment
    $ sudo docker build -t slim:test -f slim.Dockerfile .
	
## Generating tfrecord files
After preparing FER2013 dataset and slim:test, you can generate tfrecord files with following cmd:

    $ sudo nvidia-docker run -it -v /data/fer/pic:/data/pic -v /data/fer/tfrecord:/data/tfrecord /bin/bash -c "python /data/download_and_convert_data.py --dataset_dir=/data/tfrecord --dataset_name=fer --pic_path=/data/pic"

Then you will find four files in /data/fer/tfrecord, they are fer_test.tfrecord, fer_train.tfrecord, info.json and labels.txt.

Fer_test.tfrecord contains 30% pictures of the original dataset, and fer_train.tfrecord contains 70% pictures of the original dataset.
Info.json and labels.txt store information about the category information of fer2013 and the tfrecord file.

## Training
### Run Single Node Training
You can use the docker image slim:test to run slim training locally with following cmd:

    $ sudo nvidia-docker run -v /data/imagenet/tf-record/:/data/data/ -v /data/output/slim/:/data/output -it slim:test /bin/bash -c "python /data/train_image_classifier.py --data_dir=/data/data/ --output_dir=/data/output/ --num_gpus=1 --model_name=vgg_19"

You can modify the picture classification model by modifying the parameter --model_name.
You can also run this docker image on UAI Train Platform. 

For more details please see https://docs.ucloud.cn/ai/uai-train.

### Run Distributed Training
The Slim code also support distributed training. It requires a distribted training environment and a dist-config. We also provided the dist-training example code in code/train\_image\_classifier.py. 
It accepts the standard Tensorflow Dist Config from TF\_CONFIG. (To learn more about distributed training please refer to https://www.tensorflow.org/deploy/distributed). 

A standard TF\_CONFIG (compatable with the tf.estimator.Estimator API) looks like this:

    TF_CONFIG = {
    	"cluster":{
    		"master":["ip0:2222"],
    		"ps":["ip0:2223","ip1:2223"],
    		"worker":["ip1:2222"]},
    	"task":{"type":"worker","index":0},
    	"environment":"cloud"
    }

We add a func \_get\_variables\_to\_train into code/train\_image\_classifier.py to parse the TF\_CONFIG and start the ps server and worker server.

We also modify the deployment/model\_deploy.py to control the device assignment func for clone devices of DeploymentConfig:

    # Line 578 in code/deployment/model\_deploy.py
    # add task id for each replica
    if self._num_ps_tasks > 0:
      device = '%s/task:%d' % (device, self._replica_id) 

    return device


You can run the dist train with same cmd as local training:

    python /data/train_image_classifier.py --data_dir=/data/data/ --output_dir=/data/output/ --num_gpus=1 --model_name=vgg_19

Note: you should generate TF\_CONFIG for each node in the cluster.

Note: This example run the training with async-replica mode.

### Run Distributed Training On UAI Platform 
UAI Train Platform can dynamicaaly deploy the training cluster and generate the TF\_CONFIG for each training node. You only need to run the training cmd as:

    /data/train_image_classifier.py --batch_size=64 --model_name=vgg_19


### Fine-tuning a model from an existing checkpoint
Rather than training from scratch, we'll often want to start from a pre-trained model and fine-tune it.
When fine-tuning on a classification task using a different number of classes than the trained model, the new model will have a final 'logits' layer whose dimensions differ from the pre-trained model.
For this, we'll use the --checkpoint_exclude_scopes flag. This flag hinders certain variables from being loaded.
You can download various pre-trained models from [pre-trained-models](https://github.com/tensorflow/models/tree/master/research/slim#pre-trained-models).

Here is an example of how to download the resnet_v2_101 checkpoint.
```
cd /ufs/slim/fer/checkpoint
sudo wget http://download.tensorflow.org/models/resnet_v2_101_2017_04_14.tar.gz
tar -xvf resnet_v2_101_2017_04_14.tar.gz
rm resnet_v2_101_2017_04_14.tar.gz
```
Then you can train your model with resnet_v2_101 checkpoint:
```
python /data/train_image_classifier.py --data_dir=/data/data/ --output_dir=/data/output/ --num_gpus=1 --model_name=resnet_v2_101 -checkpoint_exclude_scopes=resnet_v2_101/logits --trainable_scopes=resnet_v2_101/logits
```
For more details please see https://docs.ucloud.cn/ai/uai-train.


