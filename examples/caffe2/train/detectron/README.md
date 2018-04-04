# Detectron Example
Detectron is Facebook AI Research's software system that implements state-of-the-art object detection algorithms. You can find it on https://github.com/facebookresearch/Detectron.

This example shows how to run Detectron train on UCloud UAI Train Platform. We provide the basic Detectron docker image as well as steps to run training on UAI Train Platform. There is only several simple steps.

## Setup
### Basic Detectron Docker Image

UCloud provides basic Detectron docker images through uhub.ucloud.cn/uaishare/gpu\_uaitrain\_ubuntu-16.04\_python-2.7.6\_caffe2-detectron:v1.0 (uhub.service.ucloud.cn/uaishare/gpu\_uaitrain\_ubuntu-16.04\_python-2.7.6\_caffe2-detectron:v1.0 for ucloud innernet), you can download this docker after register a UCloud account.

The image includes:

  - cudnn6.0+cuda8.0
  - caffe2 (build from master)
  - Detectron (build from master)
  - Pretrained model

Detectron is located in: /data/detectron/
Pretrained model has already been download into /data/weights/, includes R-50.pkl

### Preparing Data

You can follow https://github.com/facebookresearch/Detectron/blob/master/lib/datasets/data/README.md to get example training dataset. We can use the same dataset on UAI system, but we must make several modifications to the PATH location for convinience.

#### COCO dataset

You can download COCO data from http://cocodataset.org/#download, you should download the images and annotations and unzip them. Suppose you put your COCO dataset into /path/to/coco with following directory structure:

```
coco
|_ images
|  |_ train2017
|  |  |_ <im-1-name>.jpg
|  |  |_ ...
|  |  |_ <im-N-name>.jpg
|  |_ test2017
|  |_ ...
|_ annotations
|  |_ instances_val2017.json
   |_ instances_train2017.json
   |_ ...
```

#### PASCAL VOC dataset

You can download the VOC dataset yourself. As Detectron use coco Annotation format, you shoud the the annotation file for VOC dataset through https://storage.googleapis.com/coco-dataset/external/PASCAL_VOC.zip. Suppose you put your voc dataset into /path/to/VOCdevkit has the following directory structure:

```
VOCdevkit
|_ VOC2007
|  |_ JPEGImages
|  |  |_ <im-1-name>.jpg
|  |  |_ ...
|  |  |_ <im-N-name>.jpg
|  |_ Annotations
|  |  |_ voc_2007_trainval.json
   |  |_ voc_2007_test.json
   |  |_ ...
```


## Intro
The entry point of the training progress is in /data/detectron/tools/train\_net.py. We can use it to start the training job. The whole training job will run in docker, and we will mount the data into the docker container.

We have to prepare three things before start the training job：
1. Preparing the pretrained model and pack it into docker
2. Preparing the new dataset_catalog
3. Preparing the new training config (.yaml)

We also modify the train\_net.py to handle UAI Platform auto-generated params. This modification is included in the base detectron docker.

### Preparing your own pretrained model
You can download or use your own pretrained model. Detectron provides many pretrained models, you can download yourself. We have already put R-50.pkl and R-101.pkl to /data/weights/ inside the docker image.

For new model files, you can pack it into docker, Please see [Build Docker](#Build-your-own-docker-image) for more details

### Preparing the new dataset_catalog
As the data location in UAI Platform is different from the Detectron example (In UAI Train Docker, all data should be located in /data/data), we should modify the detectron/lib/datasets/dataset\_catalog.py to add new datasets. For example:

	#Line 28, add default uai data path prefix
	_UAI_DATA_DIR = "/data/data"

	# Available datasets
	DATASETS = {
		...

		#At the end of file
		'uai_coco_2017_train': {
	        IM_DIR:
	            _UAI_DATA_DIR + '/images/train2017',
	        ANN_FN:
	            _UAI_DATA_DIR + '/annotations/instances_train2017.json'
	    },
	    'uai_coco_2017_test': {
	        IM_DIR:
	            _UAI_DATA_DIR + '/images/test2017',
	        ANN_FN:
	            _UAI_DATA_DIR + '/annotations/image_info_test2017.json'
	    },
	    'uai_voc_2007_trainval': {
	        IM_DIR:
	            _UAI_DATA_DIR + '/VOC2007/JPEGImages',
	        ANN_FN:
	            _UAI_DATA_DIR + '/VOC2007/Annotations/voc_2007_trainval.json',
	        DEVKIT_DIR:
	            _UAI_DATA_DIR + '/VOC2007/VOCdevkit2007'
	    },
	    'uai_voc_2007_test': {
	        IM_DIR:
	            _UAI_DATA_DIR + '/VOC2007/JPEGImages',
	        ANN_FN:
	            _UAI_DATA_DIR + '/VOC2007/Annotations/voc_2007_test.json',
	        DEVKIT_DIR:
	            _UAI_DATA_DIR + '/VOC2007/VOCdevkit2007'
	    }
	}

We add coco 2017 train/test and voc 2007 train/test dataset into the dataset\_catalog.py. For other dataset, you can add yourself. Please make sure to add the \_UAI\_DATA\_DIR prefix. (You can find the modified dataset\_catalog.py code under examples/caffe2/train/detectron/)

You should pack the modified dataset\_catalog.py into docker, Please see [Build Docker](#Build-your-own-docker-image) for more details

### Preparing the new training config
We also need to modify the training config file. We have provied the example VOC2007 train yaml under examples/caffe2/train/detectron/uai\_tutorial\_1gpu\_e2e\_faster\_rcnn\_R-50-FPN.yaml, we made following changes:

	# Line 41, use local weights instead of downloading it
	WEIGHTS: "/data/weights/R-50.pkl"

	# Line 42, use voc train data
	DATASETS: ('uai_voc_2007_trainval',)

	# Line 48, use voc test data
	DATASETS: ('uai_voc_2007_test',)

	# Line 54, use /data/output as output path
	OUTPUT_DIR: "/data/output/"

Use this yaml, you can train the model using voc 2007 dataset

We also provide the examples/caffe2/train/detectron/uai\_tutorial\_1gpu\_e2e\_faster\_rcnn\_coco\_R-50-FPN.yaml for coco 2017 dataset.

### Build your own docker image
Before build our own docker image, we should prepare the directory structure:

```
/data/detectron
|_ weights
|  |_ R-50.pkl
|_ conf
|  |_ uai_tutorial_1gpu_e2e_faster_rcnn_R-50-FPN.yaml
|_ detectron_voc_example.Dockerfile

/data/example
|_ VOCdevkit
|  |_ VOC2007
```

We provided the example detectron\_voc\_example.Dockerfile for you to pack the training docker with voc 2007 dataset, you can build the docker using following CMD:

	$ cd /data/detectron
	$ sudo docker build -t detectron_voc_example:test -f detectron_voc_example.Dockerfile .

The detectron\_voc\_example.Dockerfile looks like this:

	FROM uhub.service.ucloud.cn/uaishare/gpu_uaitrain_ubuntu-16.04_python-2.7.6_caffe2-detectron:v1.0

	COPY dataset_catalog.py /data/detectron/lib/datasets/dataset_catalog.py
	COPY weights/ /data/weights/
	COPY conf/ /data/conf/

It will copy the new dataset\_catalog.py file (containing new dataset definitions) into /data/detectron/lib/datasets/, and copy the weights and conf into the docker image.

### Run locally
We can run the local training using following CMD:

	$ sudo nvidia-docker run -v /data/example/VOCdevkit/:/data/data/ -v /tmp/output/:/data/output/ -it detectron_voc_example:test /bin/bash -c "cd /data && python /data/detectron/tools/train_net.py --cfg /data/conf/uai_tutorial_1gpu_e2e_faster_rcnn_R-50-FPN.yaml"
 
### Run on UAI Train Platform
Please see https://docs.ucloud.cn/ai/uai-train/ for more information and contact our sales from ucloud.cn