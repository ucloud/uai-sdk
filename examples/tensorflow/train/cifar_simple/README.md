# cifar_Tensorflow example 
CIFAR-10 is a common benchmark in machine learning for image recognition.                                                                                      
                                                                                                                                                               
http://www.cs.toronto.edu/~kriz/cifar.html                                                                                                                     

This example uses tensorflow to implement a cnn for picture classification. 

## Original Example
Code here is an example of how to run tensorflow cifar example on UAI Train platform .                                                                    

The original code can see here: https://github.com/tensorflow/models/tree/master/tutorials/image/cifar10                                           

## Preparing  Data 
Cifar dataset will be downloaded automatically under /data/data. So you don't need to prepare data.
Also you can provide cifar data in  /data/data,so you don't need to download cifar dataset again when training model.

## build docker image 

Firstly,you can storage data according to the following structure. 
```
/_ data/
  |_ code/
  |_ cifar-cpu.Dockerfile
```
You can build docker image by Dockerfile.

```
sudo docker build -t uhub.service.ucloud.cn/YOUR_UHUB_REGISTRY/cifar_train_cpu:v1.0 -f cifar-cpu.Dockerfile .
```
So you can get a docker image named uhub.service.ucloud.cn/YOUR_UHUB_REGISTRY/cifar_train_cpu:v1.0.

## Training model 

You can run the following command to train crnn model locally.<br>
```
sudo docker run -it -v /data/data:/data/data -v data/output:/data/output /bin/bash -c "python /data/code/cifar10_train.py"

```
Cifar dataset will be downloaded automatically under /data/data. You can find checkpoint files in /data/output/.

If you have trained model locally and want to train model on UAI Train,
you should upload files under /data/data into Ucloud file storage platform such as UFile and UFS.
A detailed guidance on running training image on UAI-Train is given in:https://docs.ucloud.cn/ai/uai-train/tutorial/tf-mnist/train <br>

On UAI Train platform,you can run the following command to train crnn model.<br>
```
/data/code/cifar10_train.py
```
The program will detect whether there are cifar dataset in the path you provided automatically, if there is no cifar file , 
cifar dataset will be downloaded automatically.



