# Im2txt Example
Im2txt example shows how to run TensorFlow image captioning training on UAI Train Platform. The example is based on:
  
  https://github.com/tensorflow/models/tree/master/research/im2txt

## Origin

The Show and Tell model is a deep neural network that learns how to describe the content of images. Based on an Inception v3 model, we train the encoding layer with encoded picture data and corresponding captions. Then we fine-tune it along with the Inception v3 parameters to optimize the result. Please refer to the original page for more information and an essay on the topic.

## Intro
The im2txt training example directly uses the code in https://github.com/tensorflow/models/tree/master/research/im2txt. The training process depends on a natural language package named nltk. We provide a Dockerfile to show how to pack these python packages into the docker. 

## Preparation
Other than the source code, a docker file and a config file are offered to help pack a docker, with which you are able to run the training on UAI-Train platform. A note on the training time: to fully train an effective captioning model takes sufficient time even on GPU-packed machines, and is several times slower with CPU, so using the UAI-Train platform is recommanded. However, you can still try out the entire process locally.

You will also need the nltk package and its language package punkt. Install the nltk package: 
	
	sudo pip install -U nltk

Also, install the punkt language pack:

	python -m nltk.downloader 

If it does not work, refer to http://www.nltk.org/install.html; http://www.nltk.org/data.html

### Preparing the Data
The training requires 2 parts of data: image-caption dataset and an Inception v3 model. You should download the model, and either download or create a dataset.

Refer to https://github.com/tensorflow/models/tree/master/research/im2txt to download a workable dataset and the inception v3 model. You can also download a copy of Inception v3 model from https://github.com/tensorflow/models/tree/master/research/slim#tensorflow-slim-image-classification-library and follow the guidance below to build a self-sourced dataset.

#### Prepare self-sourced dataset
In case you intend to use your own image dataset, you should prepare several sets of data as input, including images, and captions as a json file. 
Firstly, separate your images into 2 parts: a greater collection of pictures as the training set, and a smaller collection of pictures as the validation and test set. Put the pictures in 2 separate directories under the same root.
Then, for each set of pictures, create a json file to record the captions. A json file is in the form of:

	{"images" : [{"id" : 1, "file_name" : "boy-play-skateboard.jpg"},
			{"id" : 2, "file_name" : "man-ski-on-ocean.jpg"}, 
			...
			], 
	"annotations" : [{"image_id" : 1, "caption" : "a boy play skateboard on playground."}, 
			{"image_id" : 2, "caption" : "a man ski on ocean beside boat."}, 
			...
			]
	}

For each image, you should generate a Transaction in caption\["images"] including the file name and an ID. Then, generate a transaction in caption\["annotations"] including the same ID and a caption. You can use any integers as id as long as the image file name matches its captions. generate 2 json files for training set and validation set repectively, and name them train_cap.json and val_vap.json (record the file directory and file name for training). 

For a large set of images, it is very time-consuming to create json files manually. Try to generate json files with scripts (the script is not provided), or use the dataset sourced from Internet.

You can store the data anywhere you prefer, but here we use /data/im2txt/data/ as a storage directory example. The entire data storage should be:

	|_ data/im2txt/data
	|  |_ word_counts.txt
	|  |_ train_cap.json
	|  |_ val_cap.json
	|  |_ train_img
	|  |  |_ boy-play-skateboard.jpg
	|  |  |_ man-ski-on-ocean.jpg
	... (large set of images)

	|  |_ val_img
	|  |  |_ girl-swim-in-pool.jpg
	... (small set of images)


### Data Transformation
This training example takes tf-record file as input. After preparing the dataset, transform them into tf records using the script: build_mscoco_data.py, and set the parameters to be the directories and file names. The command to create the tf-records is like below if you store the data as above: 

	python build_mscoco_data.py --train_image_dir /data/im2txt/data/train_img --val_image_dir /data/im2txt/data/val_img --train_captions_file /data/im2txt/data/train_cap.json --val_captions_file /data/im2txt/val_cap.json --output_dir /data/im2txt/data/

You should change the directory parameters to where you put the data in. You can also tinker with other parameters (check them out in the build_mscoco_data.py script), and use differently-generated tf-records as data to later examine training effectiveness. Eventually, you shall see all the tfrecords in /data/im2txt/data/ (or the directory you set as --output_dir). Put the Inception v3 model here, too.
The directory contains the following data now:

    # cd /data/im2txt/data/
    # ls
    inception_v3.ckpt
    train-00000-of-00256 train-00001-of-00256 ... train-00255-of-00256
    test-00000-of-00008 test-00001-of-00008 ... test-00007-of-00008
    val-00000-of-00004 val-00001-of-00004 ... val-00001-of-00004

containing 269 files in total.

### Build the Docker images

UCloud provides a pre-built docker image for training: im2txt-train-gpu:test. This is an image of a docker that contains the training code and all environment packages it needs, but not the datasets and the model. You can use the following docker code to pull it:

	sudo docker pull uhub.ucloud.cn/uai_demo/im2txt-train-gpu:test

Or you can do the following to build on your own. We provide the Dockerfile to build the docker image for training im2txt model written as:

    From uhub.service.ucloud.cn/uaishare/gpu_uaitrain_ubuntu-16.04_python-2.7_tensorflow-1.7.0:v1.0

    RUN pip install -U nltk
    CMD python -m nltk.downloader punkt

    ADD im2txt /data/im2txt/
    ADD ./train.py /data/
    
These ockerfile commands perform several tasks:

1. Use uaitrain-tf1.7 version as the base image of the whole docker image, which contains the tf1.7 package.
2. Install nltk, the natural language package.
3. Download the "punkt" language package of nltk.
4. Copy all the files under ./im2txt into /data/im2txt, which are the working modules of training.
5. Add train.py to the docker as the main file to be executed.

Note if you prefer to use only CPU, change the first line to:

	From uhub.service.ucloud.cn/uaishare/cpu_uaitrain_ubuntu-16.04_python-2.7_tensorflow-1.7.0:v1.0

so that the docker is built on cpu-based docker image. Otherwise it is ok to ignore the details of the docker commands.

Examine whether the entire code directory has the following files:

	/data/
	|_ train.py
	|_ uaitrain.Dockerfile
	|_ im2txt
	|  |_ __init__.py
	|  |_ configuration.py
	|  |_ show_and_tell_model.py
	|  |_ ops
	|  |  |_ __init__.py
	|  |  |_ image_embedding.py
	|  |  |_ image_embedding_test.py
	|  |  |_ image_processing.py
	|  |  |_ inputs.py

The train.py is the main script to be executed, while the scripts in directory im2txt are mainly modules and helper packages. Run the following cmd to build the image:

    sudo docker build -f uaitrain.Dockerfile -t uhub.ucloud.cn/<YOUR_UHUB_REGISTRY>/im2txt-train-gpu:test .

Note if you choose to build cpu docker earlier, you should change the suffix to "im2txt-train-cpu:test" to avoid confusion. Below we will just use gpu name as example.

This command builds the docker with the foresaid commands in the Dockerfile. You can tag the docker with any docker-name here if you want, by changing the suffix after <UHUB_REGISTRY>/, so you can manage multiple versions of dockers (e.g. you can create 2 dockers named "uhub.ucloud.cn/<YOUR_UHUB_REGISTRY>/im2txt-train-gpu:test" and "uhub.ucloud.cn/<YOUR_UHUB_REGISTRY>/im2txt-train-v2-cpu:test" respectively). After building the image, we get a docker image named uhub.ucloud.cn/<YOUR_UHUB_REGISTRY>/im2txt-train-gpu:test, which is the same as the docker provided. Check the docker image out by:

	sudo docker images

## Run the train: first phase

### Run locally
We can simply use the following command to locally test the docker. Since we built the GPU version of docker, make sure you have a GPU and relevant environment to run it on. Note that if you use any other data storage directory other than "/data/im2txt/data", you should change the same path in the parameter accordingly:
	
	-v /im2txt/data/:/data/data
	
This parameter in the command does a "map" on the directories, so that when the program goes into "/data/data/", it actually redirects into "/data/im2txt/data/" for the images and captions. Similarly, data written into "/data/output" will appear in "/data/im2txt/output". The default command to run training is:

    sudo nvidia-docker run -it -v /data/im2txt/data/:/data/data -v /data/im2txt/output/:/data/output uhub.ucloud.cn/uai_dockers/im2txt-train-gpu:test /bin/bash -c "cd /data && /usr/bin/python /data/train.py --input_file_pattern=/data/data/train-?????-of-00256 --inception_checkpoint_file=/data/data/inception_v3.ckpt --train_dir=/data/output/ --number_of_steps=1000000"

Note if you use cpu version, change "nvidia-docker" to "docker".

### Run on UAI-Train Platform
Or, more recommanded, you can run the training on UAI-Train platform with even multiple GPUs, and consume less time and computing resource. For a guidance, refer to: https://docs.ucloud.cn/ai/uai-train/tutorial/tf-mnist/train

Put the data (model and tfrecord) in UFile System for training. UFile is an online file management system (similar to a cloud) for UAI online training to read and write data, so you need to upload the generated tfrecord and inception v3 model there. The data in UFile shall look like:

	# /data/im2txt/data/
	inception_v3.ckpt
	train-00000-of-00256 train-00001-of-00256 ... train-00255-of-00256
	test-00000-of-00008 test-00001-of-00008 ... test-00007-of-00008
	val-00000-of-00004 val-00001-of-00004 ... val-00001-of-00004

So when creating the training mission, let the input path be /data/im2txt/data/, or wherever you put data, and output path be /data/im2txt/output/.

Here is the command to start the training if it is performed on UAI-Training Platform:

	/data/train.py --input_file_pattern=/data/data/train-?????-of-00256 --inception_checkpoint_file=/data/data/inception_v3.ckpt --train_dir=/data/output/ --number_of_steps=1000000

You might notice that the command is shorter than running training locally. The directory "mapping" parameters are left out because UAI-Train platform automatically applies the replacement (from the "input dir" and "output dir" to /data/data/ and /data/output/ respectly, so do not use /data/data/ and /data/output/ to store data because they will not be found). 

On the training settings, 1000000 rounds of training is experiential to generate effective model outputs. The model checkpoint after 1000000 training steps is already good enough for captioning. Refer to: https://github.com/ucloud/uai-sdk/new/master/examples/tensorflow/inference/im2txt for using the model to caption images.

### Run the train: second phase
Or instead, you can continue to fine-tune the model for even better caption results, while consuming a lot more time. For a fine-tune session, repeat the training above, but with some different parameters:

	Run locally:
	sudo nvidia-docker run -it -v /data/im2txt/data/:/data/data -v /data/im2txt/output:/data/output uhub.ucloud.cn/uai_dockers/im2txt-train-gpu:test /bin/bash -c "cd /data && /usr/bin/python /data/train.py --input_file_pattern=/data/data/train-?????-of-00256 --train_dir=/data/output/ --number_of_steps=3000000 --train_inception=true"

	Run on UAI-Train:
	/data/train.py --input_file_pattern=/data/data/train-?????-of-00256 --train_dir=/data/output/ --number_of_steps=3000000 --train_inception=true

You can just directly reuse the above docker image locally or on UAI-Train platform with or without adjusting with the datasets.

In the 2nd phase, the entire model, including inception v3 parameters, are trained altogether to fine-tune the model for more 3000000 - 1000000 = 2000000 steps. The additonal 2000000 round is yet another experiential number before the model starts to overfit. Again, you are free to try out other parameters to examine the result.

## Results
UAI Training produces the trained model containing in several files: some_model.data-00000-of-00001, some_model.meta, some_model.index and checkpoint. Now you can go to: https://github.com/ucloud/uai-sdk/tree/master/examples/tensorflow/inference/im2txt to generate captions for some pictures.

