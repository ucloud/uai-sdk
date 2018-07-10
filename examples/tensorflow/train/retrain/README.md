# Retrain Example

## Intro
Modern image recognition models have millions of parameters. Training them from scratch requires a lot of labeled training data and a lot of computing power (hundreds of GPU-hours or more). Transfer learning is a technique that shortcuts much of this by taking a piece of a model that has alreay been trained on a related task and reusing it in a new model. In this tutorial, we will reuse the feature extraction capabilities from powerful image classifiers trained on ImageNet and simply train a new classification layer on top. For more information on the approach you can see this paper on Decaf.
Though it's not as good as training the full model, this is surprisingly effective for many applications, works with moderate amounts of training data (thousands, not millions of labeled images), and can be run in as little as thirty minutes on a laptop without a GPU. This tutorial will show you how to run the example script on your own images, and will explain some of the options you have to help control the training process.
(text above from: https://www.tensorflow.org/hub/tutorials/image_retraining)

This retrain example shows how to add new layers to an object-detection model for other classification problems and run the retraining task on UAI Platform. The example is based on https://github.com/tensorflow/hub/tree/master/examples/image_retraining. 
The retrain code is identical to the source code: https://github.com/tensorflow/hub/blob/master/examples/image_retraining/retrain.py

## UAI-Train Platform
The training procedure is not far different from the the tensorflow-hub example. We introduces how to run it on UAI-Train platform which might be more efficient and resource-saving than using your own PC. As stated, the UAI-Train is offline from Internet, so you need to cache the object-detection model to local machine. Refer to https://www.tensorflow.org/hub/basics for caching module files locally.
It is compulsory to fully understand how UAI Train docker image works if you intend to use UAI-Train platform for a fast training progress. If you are not, refer to https://docs.ucloud.cn/ai/uai-train/guide/tensorflow for setup and operation guidance, or try to proceed locally with expectedly lower efficiency.

### Data Preparation
The retraining needs two parts of data, model and images. Earlier we have cached the whole module, including several files and directories:
    
    |_ data
    |  |_ checkpoint_dir
    |  |  |_ tfhub_module.pb
    |  |  |_ saved_model.pb
    |  |  |_ variables
    |  |  |_ assets
    
Then you need a set of images. Determine what objects to be detected, then find sufficient number of images for each object. Tensorflow offers a dataset of flowers: http://download.tensorflow.org/example_images/flower_photos.tgz. You may also try the dataset from http://www.robots.ox.ac.uk/%7Evgg/data/pets/, but you need to divide the image files into object types. After that, create a directory under data/images for each object, and put all images of this object into this directory, eventually with a root directory like:
    
    |_ data
    |  |_ checkpoint_dir
    |  |  |_ tfhub_module.pb
    |  |  |_ saved_model.pb
    |  |  |_ variables
    |  |  |_ assets
    |  |_ images
    |  |  |_ cat
    |  |  |  |_ cat1.jpg
    |  |  |  |_ cat2.jpg
    |  |  |  |_ cat3.jpg
    |  |  |_ chicken
    |  |  |  |_ chicken1.jpg
    |  |  |  |_ chicken2.jpg
    |  |  |  |_ chicken3.jpg

and so on. Note that the object directory's name must be the name of the object type, while the picture's name does not matter.

We put retrain codes into code/ aside to /data/. In this example we use flowers dataset(You should download the flowers data yourself) and the mobilenet_v1_100_224 object-detection module. The module offered by Tensorflow are normalized to the same file names, so any module you cache results in the same set of file names.

    # ls /data/
    flower_photos/  checkpoint_dir/
    # ls /data/flower_photos
    daisy  dandelion  roses  sunflowers  tulips
    
Now we are ready to go!

### Start Training

You can use the command line to run training locally:

    python /code/retrain_v2.py --image_dir /data/flower_photos --output_graph /data/output/frozen_inference_graph.pb --output_labels /data/output/label_map.txt --tfhub_module /data/checkpoint_dir

This training requires Tensorflow and Tensorflow-hub module. Refer to the retrain_v2.py for more parameters and training options for the retraining. 

### Start Training on UAI-Train platform

You can also use the UAI-Train platform for a much faster training with GPU. Set up the environment as:https://docs.ucloud.cn/ai/uai-train/guide/prepare

Copy the uaitrain_v2.Dockerfile outside /data and /code, and run command to pack an image: 

    sudo docker build -t uhub.ucloud.cn/<YOUR_IMAGE_REPOSITORY_NAME>/retrain-train-gpu:latest -f uaitrain_v2.Dockerfile .
    
Do not miss out the dot at the end. This is a docker image with all environments including Tensorflow, Tensorflow-hub and the retrain script built-in, and can be run either locally or on UAI-Train platform. Submit it to UHub, a cloud of images:
    
    sudo docker login uhub.ucloud.cn
    sudo docker push uhub.ucloud.cn/<YOUR_IMAGE_REPOSITORY_NAME>/retrain-train-gpu:latest
    
Then you may run it locally:

    sudo docker run -it -v /data/:/data/data/ -v /data/output/:/data/output/ uhub.ucloud.cn/<YOUR_IMAGE_REPOSITORY_NAME>/retrain-train-gpu:latest /bin/bash -c "/usr/bin/python retrain_v2.py --image_dir /data/flower_photos --output_graph /data/output/frozen_inference_graph.pb --output_labels /data/output/label_map.txt --tfhub_module /data/checkpoint_dir"

or create a Train job at console: https://console.ucloud.cn/uaitrain/manage and run the image. 
A detailed guidance on running training image on UAI-Train is given in:https://docs.ucloud.cn/ai/uai-train/tutorial/tf-mnist/train


