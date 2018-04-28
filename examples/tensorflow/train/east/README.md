# EAST Example
EAST example shows how to run tensorflow implementation of [EAST: An Efficient and Accurate Scene Text Detector](https://arxiv.org/abs/1704.03155v2) on UCloud AI Train Platform. The example is based on https://github.com/argman/EAST

# Setup
You should prepare your own training data and pretrained model before running the task. As UAI Train nodes does not provide network access, you should prepare your data locally.

## Intro
The EAST example directly use the code in https://github.com/argman/EAST. We have provided the pre-build docker image at uhub.service.ucloud.cn/uaishare/tf-east:tf-1.5

## UAI Example
We made the following modifications to the EAST code:

1.multigpu\_train.py

    # Line 7: Add UAI flag
    from uaitrain.arch.tensorflow import uflag

    # Line 72: 
    # checkpoint_path should under FLAGS.output_dir (/data/output/, the default 'UAI Train' output dir)
    # pretrained_model_path should under FLAGS.data_dir (/data/data/, the default 'UAI Train' data input dir)
    # gpus should get from FLAGS.num_gpus
    FLAGS.checkpoint_path=os.path.join(FLAGS.output_dir, FLAGS.checkpoint_path)
    if FLAGS.pretrained_model_path is not None:
        FLAGS.pretrained_model_path=os.path.join(FLAGS.data_dir, FLAGS.pretrained_model_path)
    gpus = list(range(FLAGS.num_gpus)) 

    # Line 170:
    # Add print train status every 100 steps
            if step % 100 == 0:
                end = time.time()
                avg_time_per_step = (end - start) / 100
                avg_examples_per_second = (100 * FLAGS.batch_size_per_gpu * len(gpus)) / (end - start)
                print('Step {:06d}, model loss {:.4f}, total loss {:.4f}, {:.2f} seconds/step, {:.2f} examples/second'.format(
                    step, ml, tl, avg_time_per_step, avg_examples_per_second))
                start = time.time()

2.icdar.py

    # Line 15: Add UAI flag
    from uaitrain.arch.tensorflow import uflag

    # Line 36: training_data_path should under FLAGS.data_dir (/data/data/, the default 'UAI Train' data input dir)
    FLAGS.training_data_path = os.path.join(FLAGS.data_dir, FLAGS.training_data_path)

We have provied these two modified files into east/code/.

### Preparing the Data
Please follow the https://github.com/argman/EAST/readme.md to download the training data and the pretrained model. The example use the ICDAR dataset and the slim Resnet V1 50 checkpoint.

#### Create Local Test Data Path
Suppose you have downloaded the dataset and put both the IMG files and TXT files into one dir (e.g., ICDAR 2015):

    # cd /data/east/train-data/
    # ls
    img_1.jpg img_2.jpg ... img_1000.jpg
    img_1.txt img_2.txt ... img_1000.txt

You also should put resnet\_v1\_50.ckpt in the same dir

    ```
    /data/east/
    |_ train-data
    |  |_ img_1.jpg
    |  |  img_2.jpg
    |  |  ...
    |  |  img_1000.jpg
    |  |_ img_1.txt
    |  |_ ...
    |_ |_ img_1000.txt
    |_ resnet_v1_50.ckpt
    ```

#### Preparing the EAST code for UAI Train
You should first download the code from https://github.com/argman/EAST/

    # cd /data/east/code/EAST
    # ls
    data_util.py demo_images/ ... training_samples/

Then you should substitte multigpu\_train.py and icdar.py with the one we provied.

We also have provied the pre-build image for you: uhub.service.ucloud.cn/uaishare/tf-east:tf-1.5


### Build the Docker images
We provide the basic Dockerfile to build the docker image for training east model:

    FROM uhub.service.ucloud.cn/uaishare/gpu_uaitrain_ubuntu-16.04_python-2.7.6_tensorflow-1.5.0:v1.0

    RUN apt-get update
    RUN apt-get install -y python-opencv python-tk

    RUN pip install shapely -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com

    ADD ./EAST/ /data/

You should put the east.Dockerfile into the same directory of EAST code:

    /data/east/
    |_ code
    |  |_ east.Dockerfile
    |  |_ EAST
    |  |  |_ data_util.py
    |  |  | ...
    |  |  | training_samples/
    |_ train-data
    |  |_ img_1.jpg
    |  |  img_2.jpg
    |  |  ...
    |  |  img_1000.jpg
    |  |_ img_1.txt
    |  |_ ...
    |_ |_ img_1000.txt
    |_ resnet_v1_50.ckpt

We should run the docker build under PATH\_TO/east:

    # cd /data/east/code
    # sudo docker build -f east.Dockerfile -t uhub.ucloud.cn/<YOUR_UHUB_REGISTRY>/east:test .
    
You can use any docker-name here if you want.

### Run the train
We can simply use the following cmd to run the local test.(GPU version)

    sudo nvidia-docker run -it -v /data/east/:/data/data -v /data/east/output:/data/output uhub.service.ucloud.cn/uaishare/tf-east:tf-1.5 /bin/bash -c "cd /data&&python /data/multigpu_train.py --num_gpus=1 --input_size=512 --batch_size_per_gpu=8 --text_scale=512 --training_data_path=train_data --geometry=RBOX --learning_rate=0.0001 --num_readers=24 --pretrained_model_path=resnet_v1_50.ckpt --data_dir=/data/data/ --output_dir=/data/output --checkpoint_path=east_icdar2015_resnet_v1_50_rbox
    
You can use the same image to run the training on UAI Train Platform. For more details please see https://docs.ucloud.cn/ai/uai-train.
