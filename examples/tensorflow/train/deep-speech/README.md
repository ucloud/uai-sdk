# Deep Speech Example
Deep Speech example shows how to run Deep-Speech training on UAI Train platform. Project DeepSpeech is an open source Speech-To-Text engine, using a model trained by machine learning techniques, based on Baidu's Deep Speech research paper. The example is based on https://github.com/mozilla/DeepSpeech. 

## Intro
We have provide the deep-speech docker image for you. You can use the image to run speech training directly only when you have got your data ready. 


## Deep-Speech Docker Image
The deep-speech docker images is organized as follows:

    deepspeech:tf-1.4:
        |
        |--/data/DeepSpeech/
                         |--DeepSpeech.py
                         |--data/
                             |--lm/
                                |--lm.binary
                                |--trie
                                |--vocab.txt
                         |--native_client
                         |-- <Other Files>
                         
1. We have already pack the whole DeepSpeech directory into the image under /data/DeepSpeech/
2. We have already pack the gpu command-line client into the image under /data/DeepSpeech/native_client.
3. We have already pack the lm.binary and trie file into the image under /data/DeepSpeech/data/lm/
4. We have already pack the ldc93s1 dataset into the image under /data/DeepSpeech/data/ldc93s1/
5. We made slight modifications to the DeepSpeech.py

### DeepSpeech.py
We make slight modification to DeepSpeech.py so we can run it on UAI Train platform. (As the root path for the python program lunched by UAI Train platform is /data/, we have to change its path to /data/DeepSpeech/ in the main func before running any other codes)

    def main(_):
    
      #L1813, we change the python root path to /data/DeepSpeech/
      os.chdir("/data/DeepSpeech/")
      initialize_globals()

The DeppSpeech.py inside the provied docker images has already been modified for you. We also provide the modified DeepSpeech.py in ./code/ in case you want to pack the code yourself.

## How to Get Deep Speech Docker Image
 We provide the pre-build docker image: 
    
    # In UCloud VM
    docker pull uhub.service.ucloud.cn/uaishare/deepspeech:tf-1.4
    
    # Internet
    docker pull uhub.ucloud.cn/uaishare/deepspeech:tf-1.4
    
You can also build the image by yourself, we provide the docker as deepspeech.Dockerfile.

## Run #ldc93s1 example
We have already pack the ldc93s1 example data into the docker file. You can run the following cmd to train:

    sudo nvidia-docker run -it -v /tmp/output/:/data/output/  uhub.service.ucloud.cn/uaishare/deepspeech:tf-1.4 /bin/bash -c "cd /data/&&python DeepSpeech/DeepSpeech.py --train_files /data/DeepSpeech/data/ldc93s1/ldc93s1.csv --dev_files /data/DeepSpeech/data/ldc93s1/ldc93s1.csv --test_files /data/DeepSpeech/data/ldc93s1/ldc93s1.csv --train_batch_size 1 --dev_batch_size 1 --test_batch_size 1 --n_hidden 494 --epoch 50 --checkpoint_dir /data/output/"
    
Please remember to set the --checkpoint\_dir to /data/output/, so it can be saved into host disk.

## Run Common Voice example
You should download the data yourself and preprocess it before doing the training. To get and process the data please refer to https://github.com/mozilla/DeepSpeech#common-voice-training-data.

Before running the training, you should modify the generated .csv files as follows:

1. cv-invalid.csv: Change all \<PATH_TO\>/cv\_corpus\_v1/cv-invalid/\*.wav to /data/data/cv\_corpus\_v1/cv-invalid/\*.wav
2. cv-other-dev.csv: Change all \<PATH_TO\>/cv\_corpus\_v1/cv-other-dev/\*.wav to /data/data/cv\_corpus\_v1/cv-other-dev/\*.wav
3. cv-other-test.csv: Change all \<PATH_TO\>/cv\_corpus\_v1/cv-other-test/\*.wav to /data/data/cv\_corpus\_v1/cv-other-test/\*.wav
4. cv-other-train.csv: Change all \<PATH_TO\>/cv\_corpus\_v1/cv-other-train/\*.wav to /data/data/cv\_corpus\_v1/cv-other-train/\*.wav
5. cv-valid-dev.csv: Change all \<PATH_TO\>/cv\_corpus\_v1/cv-valid-dev/\*.wav to /data/data/cv\_corpus\_v1/cv-valid-dev/\*.wav
6. cv-valid-test.csv: Change all \<PATH_TO\>/cv\_corpus\_v1/cv-valid-test/\*.wav to /data/data/cv\_corpus\_v1/cv-valid-test/\*.wav
7. cv-valid-train.csv: Change all \<PATH_TO\>/cv\_corpus\_v1/cv-valid-train/\*.wav to /data/data/cv\_corpus\_v1/cv-valid-train/\*.wav

You can run the training locally:

    sudo nvidia-docker run -it -v /data/voice/:/data/data/ -v /tmp/output/:/data/output/  uhub.service.ucloud.cn/uaishare/deepspeech:tf-1.4 /bin/bash -c "cd /data/&&python DeepSpeech/DeepSpeech.py --train_files /data/data/cv-valid-train.csv,/data/data/cv-other-train.csv --dev_files /data/data/cv-valid-dev.csv --test_files /data/data/cv-valid-test.csv --epoch 50 --checkpoint_dir /data/output/ --export_dir export_dir"
    
To run it on UAI Train, please refer to https://docs.ucloud.cn/ai/uai-train. You can simply push the image to Uhub and train data into UCloud and then run training jobs from it.