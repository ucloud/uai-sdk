# CRNN_Tensorflow example 
Use tensorflow to implement a Deep Neural Network for scene text recognition mainly based on the paper "An End-to-End Trainable Neural Network for Image-based Sequence Recognition and Its Application to Scene Text Recognition".You can refer to their paper for details http://arxiv.org/abs/1507.05717. Thanks for the author Baoguang Shi.
This model consists of a CNN stage, RNN stage and CTC loss for scene text recognition task.

## Original Example
Code here is an example of how to run CRNN_Tensorflow example on UAI Train platform.The original code can see here:https://github.com/MaybeShewill-CV/CRNN_Tensorflow/.<br>

## Preparing  Data 
### Download dataset
The model is trained on a subet of [Synth 90k](http://www.robots.ox.ac.uk/~vgg/data/text/). You should download and unzip the dataset to get trainning data.
### Preparing tfrecords
Firstly,you need to supply a txt file named sample.txt to specify the relative path to the image data dir and it's corresponding text label. For example
```
/1/2/373_coley_14845.jpg coley
/1//100_eunice_26759.jpg eunice
```
You can generate tfrecords file in a docker container. I suggest you to generate the docker image by crnn-generate-tfrecords.Dockerfile . You can storage data  according to the following structure . For example,1/2/373_coley_14845.jpg and 1/2/100_eunice_26759.jpg are examples of the training data we extracted from Synth 90k.

Because the relative path of the training data is stored in Test/sample.txt and Traing/sample.txt , Training data should be placed in the same directory as the Test and Train folders.<br>

If you want to train your own datasets,you just need to storage you datasets in the same directory as the Test and Train folders and write relative path and labels of image data in Test/sample.txt and Traing/sample.txt.
 Char_dict.json and ord_map.json must be placed in the /data/data folder . All your training image will be scaled into (32, 100, 3) , the dataset will be divided into train, test, validation set and you can change the parameter to control the ratio of them.
 If you want to use your dataset to train CRNN net , there should be only one line character in each of your images.<br>



```
/_ data/
  |_ data/
	 |_ char_dict.json
	 |_ ord_map.json
     |_ Test/
        |_ sample.txt
     |_ Train/
        |_ sample.txt
     |_ 1/
        |_ 2/
		   |_ 373_coley_14845.jpg
           |_ 100_eunice_26759.jpg
     |_ ...
  |_ code/
     |_ crnnmodel/
	 |_ data_provoder/
	 |_ global_configuration/
	 |_ local_utils/
	 |_ tools/
  |_ output/
  |_ crnn-generate-tfrecords.Dockerfile
```

You can run the following command to generate a docker image named uhub.service.ucloud.cn/uai_demo/crnn-generate-tfrecords:v1.0 to generate tfrecords file.You should change 'uai_demo' to 'YOUR_UHUB_REGISTRY'.
```
sudo docker build -t uhub.service.ucloud.cn/uai_demo/crnn-generate-tfrecords:v1.0 -f crnn-generate-tfrecords.Dockerfile .
```
In the docker image,you can generate tfrecords file locally or on UAI Training Platform .<br>
If you want to generate tfrecords file locally , you should map ./data and ./code to crnn-generate-tfrecords:v1.0 by the following command.

```
sudo docker run -it -v /data/data:/data/data -v /data/output:/data/output uhub.service.ucloud.cn/uai_demo/crnn-generate-tfrecords:v1.0
```
Then you can run the following command to generate tfrecords file locally or on UAI Training Platform .<br>
```
python /data/code/tools/write_text_features.py --dataset_dir /data/data/ --save_dir /data/output
```
If you run the command locally,you can get train_feature.tfrecords,test_feature.tfrecords and validation_feature.tfrecords in /data/output folder.
If you generate tfrecords file on UAI Training Platform,you can find tfrecords file on Ucloud file storage platform such as UFile and UFS.

## Training model 
Firstly,you can storage data according to the following structure. 
```
|_ data/
  |_ data/
     |_ train_feature.tfrecords
	 |_ test_feature.tfrecords
	 |_ validation_feature.tfrecords
	 |_ char_dict.json
	 |_ ord_map.json
  |_ code/
     |_ crnnmodel/
	 |_ data_provoder/
	 |_ global_configuration/
	 |_ local_utils/
	 |_ tools/
  |_ ocr-cpu.Dockerfile 
```
You can build docker image by Dockerfile.

```
sudo docker build -t uhub.service.ucloud.cn/uai_demo/ocr_test:v1.0 -f ocr-cpu.Dockerfile .
```
So you can get a docker image named uhub.service.ucloud.cn/uai_demo/ocr_test:v1.0.You should change 'uai_demo' to 'YOUR_UHUB_REGISTRY'.<br>
About training parameters you can check the global_configuration/config.py for details.<br>
you can run the following command to train crnn model.<br>
```
python /data/code/tools/train_shadownet.py  --dataset_dir /data/data
```
If you want to train a model on UAI Train,you should build docker image by ocr-gpu.Dockerfile and upload the following data into Ucloud file storage platform such as UFile and UFS.
```
     |_ train_feature.tfrecords
	 |_ test_feature.tfrecords
	 |_ validation_feature.tfrecords
	 |_ char_dict.json
	 |_ ord_map.json
```


