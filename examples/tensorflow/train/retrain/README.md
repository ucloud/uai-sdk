# Retrain Example

## Intro
Modern image recognition models have millions of parameters. Training them from scratch requires a lot of labeled training data and a lot of computing power (hundreds of GPU-hours or more). Transfer learning is a technique that shortcuts much of this by taking a piece of a model that has alreay been trained on a related task and reusing it in a new model. In this tutorial, we will reuse the feature extraction capabilities from powerful image classifiers trained on ImageNet and simply train a new classification layer on top. For more information on the approach you can see this paper on Decaf.

Though it's not as good as training the full model, this is surprisingly effective for many applications, works with moderate amounts of training data (thousands, not millions of labeled images), and can be run in as little as thirty minutes on a laptop without a GPU. This tutorial will show you how to run the example script on your own images, and will explain some of the options you have to help control the training process.
(text above from: https://www.tensorflow.org/hub/tutorials/image_retraining)

This retrain example shows how to add new layers to an object-classification model for other classification problems and run the retraining task on UAI Platform. The example is based on https://github.com/tensorflow/hub/tree/master/examples/image_retraining. 
The retrain code is identical to the source code: https://github.com/tensorflow/hub/blob/master/examples/image_retraining/retrain.py

## UAI-Train Platform
The training procedure is not far different from the the tensorflow-hub example. We introduces how to run it on UAI-Train platform which might be more efficient and resource-saving than using your own PC. As stated, the UAI-Train platform has no access to Internet, so you need to cache the object-classification model to local machine. 
You are suggested to setup docker and uai-sdk environment as https://docs.ucloud.cn/ai/uai-train/guide/tensorflow, or just try to proceed locally with expectedly lower efficiency.

### Data Preparation
The retraining needs two parts of data, model and images. Select a module based on your requirement of accuracy and time consumption, and cache it to local machine, including several files and directories (refer to https://www.tensorflow.org/hub/basics for caching module files locally):
    
    |_ /data/model_and_images
    |  |_ checkpoint_dir
    |  |  |_ tfhub_module.pb
    |  |  |_ saved_model.pb
    |  |  |_ variables
    |  |  |_ assets
    
Pay attention to what type of models you are caching. The Tensorflow website offers classification and feature vector models. We use the classification module to do object classification. Feature vector model extracts the features of objects and may be useful in many AI cases, but is not used here.

Then you need a set of images. Determine what objects to be classified, then find sufficient number of images for each object. Tensorflow offers a dataset of flowers: http://download.tensorflow.org/example_images/flower_photos.tgz. You may also try the dataset from http://www.robots.ox.ac.uk/%7Evgg/data/pets/, but you need to divide the image files into object types. After that, create a directory under data/images for each object, and put all images of this object into this directory, eventually with a root directory like:
    
    |_ /data/model_and_images
    |  |_ checkpoint_dir
    |  |  |_ tfhub_module.pb
    |  |  |_ saved_model.pb
    |  |  |_ variables
    |  |  |_ assets
    |  |_ flower_photos
    |  |  |_ daisy
    |  |  |  |_ daisy1.jpg
    |  |  |  |_ daisy2.jpg
    |  |  |  |_ daisy3.jpg
    |  |  |_ roses
    |  |  |  |_ roses1.jpg
    |  |  |  |_ roses2.jpg
    |  |  |  |_ roses3.jpg

and so on. Note that the object directory's name must be the name of the object type, while the picture's name does not matter.

We put retrain codes into code/ aside to /data/. In this example we use flowers dataset(You should download the flowers data yourself) and the mobilenet_v1_100_224 object-classification module. The module offered by Tensorflow are normalized to the same file names, so any module you cache results in the same set of file names.

    # ls /data/
    model_and_images/ code/
    # ls /data/code/
    retrain_v2.py
    # ls /data/model_and_images/flower_photos
    daisy  dandelion  roses  sunflowers  tulips
    
Now we are ready to go!

### Start Training

You can use the command line to run training locally:

    python /data/code/retrain_v2.py --image_dir /data/model_and_images/flower_photos --output_graph /data/output/frozen_inference_graph.pb --output_labels /data/output/label_map.txt --tfhub_module /data/model_and_images/checkpoint_dir

This training requires Tensorflow and Tensorflow-hub module. Refer to the retrain_v2.py for more parameters and training options for the retraining. 

### Start Training on UAI-Train platform

You can also use the UAI-Train platform for a much faster training with GPU. Set up the environment as:https://docs.ucloud.cn/ai/uai-train/guide/prepare

Copy the uaitrain_v2.Dockerfile into /data, change directory to /data, and run command to pack an image: 

    sudo docker build -t uhub.ucloud.cn/<YOUR_IMAGE_REPOSITORY_NAME>/retrain-train-gpu:latest -f uaitrain_v2.Dockerfile .
    
Do not miss out the dot at the end. This is a docker image with all environments including Tensorflow, Tensorflow-hub and the retrain script built-in, and can be run either locally or on UAI-Train platform. Submit it to UHub, a cloud of images:
    
    sudo docker login uhub.ucloud.cn
    sudo docker push uhub.ucloud.cn/<YOUR_IMAGE_REPOSITORY_NAME>/retrain-train-gpu:latest
    
Then you may run it locally:

    sudo docker run -it -v /data/label_and_images/:/data/data/ -v /data/output/:/data/output/ uhub.ucloud.cn/<YOUR_IMAGE_REPOSITORY_NAME>/retrain-train-gpu:latest /bin/bash -c "/usr/bin/python /data/retrain_v2.py --image_dir /data/data/flower_photos --output_graph /data/output/frozen_inference_graph.pb --output_labels /data/output/label_map.txt --tfhub_module /data/data/checkpoint_dir"

You are suggested to create a Train job at console: https://console.ucloud.cn/uaitrain/manage and run the image. Check https://docs.ucloud.cn/ai/uai-train/tutorial/tf-mnist/train for an example of using the console, including how to upload required data to UFile, a file system provided for the UAI-Training and UAI-Inference. 

While running on UAI-Train console, set the input directory to UFile: /data/label_and_images/, and output directory to UFile: /data/output/, and training command to: 

    /data/retrain_v2.py --image_dir /data/data/flower_photos --output_graph /data/output/frozen_inference_graph.pb --output_labels /data/output/label_map.txt --tfhub_module /data/data/checkpoint_dir

A detailed guidance on running training image on UAI-Train is given in:https://docs.ucloud.cn/ai/uai-train/tutorial/tf-mnist/train

### Use the Retrained Model
Here in uai-sdk we have an example on how to use the retrained model for object classification: https://github.com/ucloud/uai-sdk/tree/master/examples/tensorflow/inference/retrain, where you can re-use the trained model to actually classify something.

It is also based on, and a demonstration of, a tensorflow example of how these AI tasks can remotely and efficiently run on UAI platform. The original idea is from: https://www.tensorflow.org/hub/tutorials/image_retraining



