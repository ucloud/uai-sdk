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
  |_ crnn-cpu.Dockerfile
  |_ crnn-gpu.Dockerfile
```

Tneh you can build a cpu docker image by crnn-cpu.Dockerfile.

```
sudo docker build -t uhub.service.ucloud.cn/YOUR_UHUB_REGISTRY/crnn_cpu -f ocr-cpu.Dockerfile .
```
You can also build a gpu docker image by crnn-gpu.Dockerfile.
```
sudo docker build -t uhub.service.ucloud.cn/YOUR_UHUB_REGISTRY/crnn_gpu -f ocr-gpu.Dockerfile .
```

 
## Preparing  Data
We need to generate pictures by ourselves to get trainning data.In this example,we used the [Poem dataset of THU Open Chinese Lexicon](http://thuocl.thunlp.org/#shici) as our training corpus.We need to generate four files,they are 1.images for training 2.sample.txt 3.a txt file which stores characters 4. char_dict
### Generate training images
First,you should storage Poem dataset and font under /data/data/gen_data/.
You can generate pictures for training by running the following command
```
sudo docker run -it -v /data/data:/data/data uhub.service.ucloud.cn/uai_demo/crnn_cpu:latest /bin/bash -c "python /data/code/gen_data/gen_pic.py --font_path='/data/data/gen_data/MSYHL.TTC'"
```
You can change font by '--font_path'.
Pictures for training can be found under /data/data/pic.

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

### Generate character txt file 
You need to generate a character txt to store all characters of poem dataset.
You can generate character txt file by following command:
```
sudo docker run -it -v /data/data:/data/data uhub.service.ucloud.cn/uai_demo/crnn_cpu:latest /bin/bash -c "python /data/code/gen_data/gen_chinesetxt.py"
```
### Generate char_dict files

By running following command,char_dict.json、index_2_ord_map.json and ord_2_index_map.json will be generated under char_dict/.
These three files describe the relationship between the encoding of characters and the index of characters in training.
```
sudo docker run -it -v /data/data:/data/data uhub.service.ucloud.cn/uai_demo/crnn_cpu:latest /bin/bash -c "python /data/code/tools/establish_char_dict.py"
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
sudo docker run -it -v /data/data:/data/data -v /data/output:/data/output  uhub.service.ucloud.cn/uai_demo/crnn_cpu:latest  /bin/bash -c "/usr/bin/python /data/code/tools/train_shadownet.py"
```
The checkpoint files will be storaged under /data/output.

### Training model on UAI-Train platform
first,you should upload files under /data/data into Ucloud file storage platform such as UFile and UFS.
A detailed guidance on running training image on UAI-Train is given in:https://docs.ucloud.cn/ai/uai-train/tutorial/tf-mnist/train <br>

On UAI Train platform,you can run the following command to train crnn model.<br>
```
/data/code/tools/train_shadownet.py 
```


