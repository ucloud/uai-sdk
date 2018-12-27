# ArcFace Example
This example shows how to run insightface/ArcFace training on UAI Platform. The example provides an implementation of running the training using softmax loss on a distributed environment.

## Intro
This example follows the implementation in https://github.com/deepinsight/insightface. We only provide a distributed training implementation of ArcFace here in code/train\_softmax\_dist.py. The modules train\_softmax\_dist.py depends are identical to those in https://github.com/deepinsight/insightface.

## Setup
You should follow https://github.com/deepinsight/insightface to download the training dataset and setup the code.

You can put the insightface code into one directory and put code/train\_softmax\_dist.py into the same directory, for example:

    /example/insightface/code/
    |_ src/
    |  |_ train_softmax.py
    |  |_ train_softmax_multi.py
    |  |_ data.py
    |  |_ align/
    |  |_ api/
    |  |_ common/
    |  |_ ...
    |  |_ utils/
    |_ ...
    
This example use the data of https://github.com/deepinsight/insightface/wiki/Dataset-Zoo DeepGlint.

## UAI Example  
                                                                                                                                               
### Supporting UAI Platform
We add five arguments for auto-generated args of UAI Platform:

	parser.add_argument('--work_dir', type=str, default="/data", help='Default work path')
	parser.add_argument('--output_dir', type=str, default="/data/output", help="Default output path")
	parser.add_argument('--log_dir', type=str, default="/data/output", help="Default log path")
	parser.add_argument('--num_gpus', type=int, help="Num of avaliable gpus")
	parser.add_argument('--data_dir', default='', help='training set directory')

It defines the default code/data/output path of running a task on UAI Platform as well as the number of gpus the GPU node provides.

### Supporting Distributed Training
We add three arguments for mxnet distributed training:

    parser.add_argument('--kv-store', type=str, default='device', help='key-value store type')
    parser.add_argument('--gc-type', type=str, default='none',
                       help='type of gradient compression to use, takes `2bit` or `none` for now')
    parser.add_argument('--optimizer', type=str, default='sgd', help='the optimizer type')
    
We also change how models are saved and restored. We save the model every epoch instead of every N steps. We also add code to setup kvstore for distributed training. For more details please refer to code/train\_softmax\_dist.py

Note: Sphere Loss is not sutiable for distributed training.

### Build Training Docker Image
We have provided insightface.Dockerfile to build the docker image for training. You can put the dockerfile into the same directory as the code as:

	/example/
    |_ insightface.Dockerfile
    |_ insightface/code/
    |_ src/
    |  |_ train_softmax.py
    |  |_ train_softmax_multi.py
    |  |_ ...
    |_ ...
    
And run the following cmd to build the docker

	sudo docker build -f insightface.Dockerfile -t insightface_dist:test .
	
You can use insightface_dist:test for training. For single node training, the entry is code/train\_softmax.py. For distributed training, the entry is code/train\_softmax\_multi.py.

### Run training locally
To run/test the docker image locally, you can use following cmd:

	sudo docker run -it -v /PATH_TO_TRAIN_DATA/:/data/data/ -v /PATH_TO_OUTPUT/:/data/output insightface_dist:test /bin/bash -c "cd /data/&&python src/train_softmax.py --num_gpus=1 --network r50 --loss-type 4 --margin-m 0.5 --prefix /data/output/model-r50-aceFace --per-batch-size=64"
	
You should put the data (e.g., faces_glint/ of DeepGlint) into /PATH\_TO\_TRAIN\_DATA/. The result model will be output to /PATH\_TO\_OUTPUT/.

### Running Distributed Training
UAI Platform provides an automatic mxnet distributed training environment configurate. We can directly start distributed training by using UAI Train Platform.

You can tag docker image as follows and push it into UCloud Docker Hub:

    sudo docker tag insightface_dist:test -t uhub.ucloud.cn/YOUR_BUCKET_NAME/insightface_dist:test
    sudo docker push uhub.ucloud.cn/YOUR_BUCKET_NAME/insightface_dist:test
    
And start distributed training with following cmds (We use dist_sync for kv-store in this example, and try to load a pretrained model with prefix of /data/output/model-r50-aceFace with epoch 2):

	src/train_softmax_multi.py --network r50 --loss-type 4 --margin-m 0.5 --prefix /data/output/model-r50-aceFace --per-batch-size=256 --kv-store=dist_sync --pretrained=/data/output/model-r50-aceFace,2
	
To run it in private distributed environment, you should add additional args to the cmd line and start the cluster yourself: 

	--num_gpus=N How many GPUs each node have.
	--data_dir=/data/ The location of your training data