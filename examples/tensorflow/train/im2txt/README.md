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

	python -m nltk.downloader nltk

If it does not work, refer to http://www.nltk.org/install.html; http://www.nltk.org/data.html

### Preparing the Data
The training requires 2 parts of data: image-caption dataset and an Inception v3 model.
You should prepare the training data and an Inception v3 model before running the task. As UAI Train nodes does not provide Internet access, you should prepare your data locally (either download or generate).
You could refer to https://github.com/tensorflow/models/tree/master/research/im2txt to download a workable dataset and the inception v3 model. It is also ok to secure a copy of Inception v3 model from other sources and follow the guidance below to build a self-sourced dataset.

#### Prepare self-sourced dataset
In case you intend to use your own image dataset, you should prepare several sets of data as input, including images and captions as a json file. 
Firstly, separate your images into 2 parts: a greater collection of pictures as the training set, and a smaller collection of pictures as the validation and test set. Put the pictures in 2 separate directories under the same root.
Then, for each set of pictures, create a json file to record the captions. A json file is in the form of:

	{"images" : [{"id" : 1, "file_name" : "boy-play-skateboard.jpg"},
			{"id" : 2, "file_name" : "man-ski-on-ocean.jpg"}, 
			...], 
	"annotations" : [{"image_id" : 1, "caption" : "a boy play skateboard on playground."}, 
			{"image_id" : 2, "caption" : "a man ski on ocean beside boat."}, 
			...]
	}

You can use any integers as id as long as the image file name matches its captions. generate 2 json files for training set and validation set separately, and name them train_cap.json and val_vap.json (record the file directory and file name for training). 
For a large set of images, it is seemingly impossible to create json files mannually, so please try to generate json files with scripts, or use the dataset sourced from Internet.

The entire data storage should be:

	|_ data/im2txt
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


### Create Local Test Data Path
Prepare the dataset and transform them into tf records using the script: build_mscoco_data.py, and set the parameters to be the directories and file names as above.

Put all the tfrecord and the Inception v3 model checkpoint into /data/im2txt/data/.
The directory contains the following data:

    # cd /data/im2txt/data/
    # ls
    inception_v3.ckpt
    train-00000-of-00256 train-00001-of-00256 ... train-00255-of-00256
    test-00000-of-00008 test-00001-of-00008 ... test-00007-of-00008
    val-00000-of-00004 val-00001-of-00004 ... val-00001-of-00004

269 files in total.

### Build the Docker images

UCloud provides a pre-built docker image for training: im2txt-train-gpu:test. This is an image of a docker that contains the training code and all environment packages it needs, but not the datasets and the model. You can use the following docker code to pull it:

	sudo docker pull uhub.ucloud.cn/uai_demo/im2txt-train-gpu:test

Or you can do the following to build on your own. We provide the basic Dockerfile to build the docker image for training im2txt model written as:

    From uhub.service.ucloud.cn/uaishare/gpu_uaitrain_ubuntu-16.04_python-2.7_tensorflow-1.7.0:v1.0

    RUN pip install -U nltk
    CMD python -m nltk.downloader punkt

    ADD im2txt /data/im2txt/
    ADD ./train.py /data/
    
The above dockerfile commands perform several tasks:

1. Use uaitrain-tf1.7 version as the base image of the whole docker image, which contains the tf1.7 package.
2. Install nltk, the natural language package.
3. Download the "punkt" language package of nltk.
4. Copy all the files under ./im2txt into /data/im2txt, which are the working modules of training.
5. Add train.py to the docker as the main file to be executed.

Put the above docker file in the same directory of train.py. Run the following cmd to build the image:

    sudo docker build -f uaitrain.Dockerfile -t uhub.ucloud.cn/<YOUR_UHUB_REGISTRY>/im2txt-train-gpu:test .

These commands build the docker with the above commands in the Dockerfile. You can use tag the docker with any docker-name here if you want by changing the suffix after <UHUB_REGISTRY>/, so you can manage multiple versions of dockers without confusion. After building the image, we get a docker image named uhub.ucloud.cn/<YOUR_UHUB_REGISTRY>/im2txt-train-gpu:test, which is the same as the docker provided.

## Run the train: first phase

We can simply use the following command to run the local test(GPU version). Make sure you have a GPU and relevant environment to run it on. Note that if you use any other data storage directory other than "/data/im2txt/data", you should change the same path in the command accordingly. The parameter:
	
	-v /im2txt/data/:/data/data
	
replaces the directories, so that when the program goes to "/data/data/", it actually redirects into "/data/im2txt/data/" for the images and captions. Here is the default command:

    sudo nvidia-docker run -it -v /data/im2txt/data/:/data/data -v /data/im2txt/output:/data/output uhub.ucloud.cn/uai_dockers/im2txt-train-gpu:test /bin/bash -c "cd /data && /usr/bin/python /data/train.py --input_file_pattern=/data/data/train-?????-of-00256 --inception_checkpoint_file=/data/data/inception_v3.ckpt --train_dir=/data/output/ --number_of_steps=1000000"

Or, recommandedly, you can run the training on UAI-Train platform. For a guidance: https://docs.ucloud.cn/ai/uai-train/tutorial/tf-mnist/train
Here is the command to start the training if it is performed on UAI-Training Platform:

	/data/train.py --input_file_pattern=/data/data/train-?????-of-00256 --inception_checkpoint_file=/data/data/inception_v3.ckpt --train_dir=/data/output/ --number_of_steps=1000000

Note here that some directory replacement parameters are left out because UAI-Train platform forcingly applies the replacement (to /data/data/ and /data/output/ respectly, so do not use these 2 directories to store data because they will not be found). Let the input path be /data/im2txt/data/, or wherever you put data, and output path be /data/im2txt/output/. The input tf records and checkpoint and the output model should be in UFile system if you use the UAI-Train system.

On the training settings, 1000000 rounds of training is experiential to generate effective model outputs. The model checkpoint after 1000000 training steps is already good enough for captioning. Refer to: https://github.com/ucloud/uai-sdk/new/master/examples/tensorflow/inference/im2txt for using the model to caption images.

### Run the train: second phase
Or instead, you can continue to fine-tune the model for even better caption results, while consuming a lot more time. For a fine-tune session, repeat the training above, but with some different parameters:

	Run locally:
	sudo nvidia-docker run -it -v /data/im2txt/data/:/data/data -v /data/im2txt/output:/data/output uhub.ucloud.cn/uai_dockers/im2txt-train-gpu:test /bin/bash -c "cd /data && /usr/bin/python /data/train.py --input_file_pattern=/data/data/train-?????-of-00256 --train_dir=/data/output/ --number_of_steps=3000000 --train_inception=true"

	Run on UAI-Train:
	/data/train.py --input_file_pattern=/data/data/train-?????-of-00256 --train_dir=/data/output/ --number_of_steps=3000000 --train_inception=true

You can just directly run the above docker image locally or on UAI-Train platform without tinkering with the datasets.

In the 2nd phase, the entire model, including inception v3 parameters, are trained altogether to fine-tune the model for more 3000000 - 1000000 = 2000000 steps. The additonal 2000000 round is yet another experiential number before the model starts to overfit. Again, you are free to try out other parameters to examine the result.

## Results
UAI Training produces the trained model containing in several files: some_model.data-00000-of-00001, some_model.meta, some_model.index and checkpoint. Now you can go to: https://github.com/ucloud/uai-sdk/tree/master/examples/tensorflow/inference/im2txt to generate captions for some pictures.

