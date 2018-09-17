# CRNN_Tensorflow example 
Use tensorflow to implement a Deep Neural Network for scene text recognition mainly based on the paper "An End-to-End Trainable Neural Network for Image-based Sequence Recognition and Its Application to Scene Text Recognition".You can refer to their paper for details http://arxiv.org/abs/1507.05717. Thanks for the author Baoguang Shi.
This model consists of a CNN stage, RNN stage and CTC loss for scene text recognition task.

## Original Example
Code here is an example of how to run CRNN_Tensorflow example on UAI Train platform.The original code can see here:https://github.com/MaybeShewill-CV/CRNN_Tensorflow/.<br>

## Preparing docker image
We will generate training data by a docker image.You can download the docker image we have prepared by the following command.
```
sudo docker pull uhub.service.ucloud.cn/uai_demo/crnn_cpu:latest
sudo docker pull uhub.service.ucloud.cn/uai_demo/crnn_gpu:latest
```

You can also build a docker image by yourself.You should storage data according to the following structure firstly.
```
/_ build/
  |_ code/
    |_ crnn_model/
    |_ data_provoder/
    |_ global_configuration/
    |_ local_utils/
    |_ tools/
    |_ gen_data/
  |_ code_multi/
    |_ tools
  |_ crnn-cpu.Dockerfile
  |_ crnn-gpu.Dockerfile
  |_ crnn-multi-gpu.Dockerfile
```

Then you can build a cpu docker image by crnn-cpu.Dockerfile.
```
sudo docker build -t uhub.service.ucloud.cn/YOUR_UHUB_REGISTRY/crnn_cpu -f ocr-cpu.Dockerfile .
```
You can also build a gpu docker image by crnn-gpu.Dockerfile.
```
sudo docker build -t uhub.service.ucloud.cn/YOUR_UHUB_REGISTRY/crnn_gpu -f ocr-gpu.Dockerfile .
```

 
## Preparing  Data
We need to generate pictures by ourselves to get trainning data.In this example,we used the [Poem dataset of THU Open Chinese Lexicon](http://thuocl.thunlp.org/#shici) as our training corpus.We need to generate four files,they are 

  1. Generating images for training 
  2. Generating sample.txt 
  3. Generating a txt file which stores characters 
  4. Generating char_dict

If you have already got the training images and its corresponding labels, you should skip the step 1, step 2 and step 3, but you should generate sample.txt according to the format in [Generate sample.txt](#generate-sample-txt) and generate chinese.txt according to the format in [Generate character txt file](#generate-character-txt-file). Step 4 will generate char_dict used in training for you.

### Generate training images
We provide scripts to automatically generating training images from texts. The code is under crnn_chinese/code/gen_data/. In this example, we provide the THUOCL_poem.txt for you. We also provide a font file MSYHL.TTC for you.

First,you should storage Poem dataset and font under /data/data/gen_data/
```
  /data/data/gen_data/
  |_ THUOCL_poem.txt
  |_ MSYHL.TTC
```

You can generate pictures for training by running the following command
```
sudo docker run -it -v /data/data:/data/data uhub.service.ucloud.cn/uai_demo/crnn_cpu:latest /bin/bash -c "python /data/code/gen_data/gen_pic.py --font_path='/data/data/gen_data/MSYHL.TTC'"
```
You can change font by '--font_path'.
Pictures for training can be found under /data/data/pic.

Note: You can modify the gen_pic.py to generate images with more noises.

### Generate sample.txt
You should generate two sample.txt files which store the relative path of pictures and their labels. The following line is an example of sample.txt.
```
pic/1679/14_0.jpg 一日难再晨
```

You can run the following command to generate sample.txt.
```
sudo docker run -it -v /data/data:/data/data uhub.service.ucloud.cn/uai_demo/crnn_cpu:latest /bin/bash -c "python /data/code/gen_data/gen_sample.py"
```
You can find sample.txt you have generated under /data/data/Train and /data/data/Test.

If you want to generate sample.txt according to your own training data. You should write your own script and follow the above sample.txt format.

### Generate character txt file 
You need to generate a character txt to store all characters of poem dataset. Now we need to get all char(chinese char) from THUOCL_poem.txt and format them into one file in the following format(One charactor each line:

```
古
节
本
术
可
```

You can generate character txt file by following command:
```
sudo docker run -it -v /data/data:/data/data uhub.service.ucloud.cn/uai_demo/crnn_cpu:latest /bin/bash -c "python /data/code/gen_data/gen_chinesetxt.py"
```

### Generate char_dict files
Now the data path containing following data
```
  /data/data/
  |_ gen_data/
     |_ THUOCL_poem.txt
     |_ MSYHL.TTC
  |_ Train
     |_ sample.txt
  |_ Test
     |_ sample.txt
  |_ pic
  |_ chinese.txt
```

By running following command,char_dict.json、index_2_ord_map.json and ord_2_index_map.json will be generated under char_dict/.
These three files describe the relationship between the encoding of characters and the index of characters in training.
```
sudo docker run -it -v /data/data:/data/data uhub.service.ucloud.cn/uai_demo/crnn_cpu:latest /bin/bash -c "python /data/code/tools/establish_char_dict.py --char_dict_file /data/data/chinese.txt"
```

## Preparing tfrecords
You can generate tfrecords files by uhub.service.ucloud.cn/YOUR_UHUB_REGISTRY/crnn_cpu.
Firstly,you need to storage data according to the following structure.
```
/_ data/
  |_ data/
    |_ char_dict/
      |_ char_dict.json
      |_ index_2_ord_map.json
      |_ ord_2_index_map.json
    |_ Test/
      |_ sample.txt
    |_ Train/
      |_ sample.txt
    |_ pic/
 |_ tfrecords
```
Run following command to generate tfrecords files.
```
sudo docker run -it -v /data/data:/data/data -v /data/data/tfrecords:/data/output uhub.service.ucloud.cn/uai_demo/crnn_cpu:latest  /bin/bash -c " /usr/bin/python /data/code/tools/write_text_tfrecords.py  --batch_size=10000"
```
The tfrecords files you have generated will be storaged under /data/tfrecords/

## Training model 

### Training model locally
Before training model on UAI-Train platform,you can first train model locally.
```
sudo docker run -it -v /data/data:/data/data -v /data/output:/data/output  uhub.service.ucloud.cn/uai_demo/crnn_cpu:latest  /bin/bash -c "/usr/bin/python /data/tools/train_shadownet.py"
```
The checkpoint files will be storaged under /data/output.

### Training model on UAI-Train platform
First,you should upload files under /data/data into Ucloud file storage platform such as UFile and UFS.
A detailed guidance on running training image on UAI-Train is given in:https://docs.ucloud.cn/ai/uai-train/tutorial/tf-mnist/train

On UAI Train platform,you can run the following command to train crnn model.
```
/data/tools/train_shadownet.py 
```

## Training with multi-gpu
We also provide code for multi-gpu/distributed training in code\_multi/tools/train\_shadownet\_multi.py. You can run it on a multi-gpu platform such as UAI Train multi-gpu node. 

You can build a crnn multi-gpu docker image by crnn-multi-gpu.Dockerfile.
```
sudo docker build -t uhub.service.ucloud.cn/YOUR_UHUB_REGISTRY/crnn_multi_gpu -f crnn-multi-gpu.Dockerfile .
```

The train\_shadownet\_multi.py takes the num\_gpus arguments as the number of gpus the training used. You can also run it locally with 4 gpus:
```
sudo docker run -it -v /data/data:/data/data -v /data/output:/data/output  uhub.service.ucloud.cn/YOUR_UHUB_REGISTRY/crnn_multi_gpu:latest  /bin/bash -c "/usr/bin/python /data/code/tools/train_shadownet.py --num_gpus=4"
```

We also add some params for convenience of modifying training parameters. We also add a L2 normalization for LSTM weight. The tfrecod format, char_dict.json, index_2_ord_map.json and ord_2_index_map.json are same as single-gpu run. But it depends on the tools/shadownet.py to load tfrecod data.

## Training with distributed multi-gpu
train\_shadownet\_multi.py can also be used in distributed training envs. (It is implemented with tensorflow Estimator interface.) 

UAI Train Platform can dynamicaaly deploy the training cluster and generate the TF\_CONFIG for each training node. You only need to run the training cmd as:

    /data/tools/train_shadownet_multi.py --steps=200000 --tfrecord_dir="tfrecords"

For more details please see https://docs.ucloud.cn/ai/uai-train.
