# cifar_Tensorflow example 
CIFAR-10 is a common benchmark in machine learning for image recognition.                                                                                      
                                                                                                                                                               
http://www.cs.toronto.edu/~kriz/cifar.html                                                                                                                     

This example uses tensorflow to implement a cnn model for picture classification. 

## Original Example
Code here is an example of how to run tensorflow cifar example on UAI Train platform .                                                                    

The original code can see here: https://github.com/tensorflow/models/tree/master/tutorials/image/cifar10                                           

## Build docker image 

Firstly,you can storage data according to the following structure. 
```
/_ data/
  |_ code/
  |_ cifar-cpu.Dockerfile
  |_ cifar-gpu.Dockerfile
```
You can build docker image by Dockerfile.

```
sudo docker build -t uhub.service.ucloud.cn/YOUR_UHUB_REGISTRY/cifar_train_cpu:v1.0 -f cifar-cpu.Dockerfile .
```
So you can get a docker image named uhub.service.ucloud.cn/YOUR_UHUB_REGISTRY/cifar_train_cpu:v1.0.

You can also get a gpu docker image named uhub.service.ucloud.cn/YOUR_UHUB_REGISTRY/cifar_train_gpu:v1.0 by running the following command.

```
sudo docker build -t uhub.service.ucloud.cn/YOUR_UHUB_REGISTRY/cifar_train_gpu:v1.0 -f cifar-gpu.Dockerfile .
```

## Preparing  Data 

By running the following command locally,cifar dataset will be downloaded into /data/data.

```
sudo docker run -it -v /data/data:/data/data  uhub.service.ucloud.cn/YOUR_UHUB_REGISTRY/cifar_train_cpu:v1.0 /bin/bash -c "python /data/data/download.py"
```
download.py should be placed into /data/data.Content of download.py is as follows:
```
import cifar10
cifar10.maybe_download_and_extract()
```


## Training model 

You can run the following command to train cifar model locally.<br>
```
sudo docker run -it -v /data/data:/data/data -v data/output:/data/output uhub.service.ucloud.cn/YOUR_UHUB_REGISTRY/cifar_train_cpu:v1.0 /bin/bash -c "python /data/code/cifar10_train.py"
```
You can find checkpoint files in /data/output/.

If you want to train model on UAI Train,
you should upload files under /data/data into Ucloud file storage platform such as UFile and UFS.

A detailed guidance on running training image on UAI-Train is given in:https://docs.ucloud.cn/ai/uai-train/tutorial/tf-mnist/train <br>

On UAI Train platform,you can run the following command to train cifar model.<br>
```
/data/code/cifar10_train.py
```



