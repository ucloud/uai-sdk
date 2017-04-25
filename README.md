# uai-sdk
UCloud AI service SDK
This SDK include basic APIs to run AI inference services on a http server.
It currently only support tensorflow, we will continue to add more platform into it.

## Supported AI Platform
Tensorflow (0.11 tested)

## How to install
1. Install Tensorflow (0.11 prefered)
2. Install UCloud Ufile SDK (https://docs.ucloud.cn/storage_cdn/ufile/tools)

        $ wget http://sdk.ufile.ucloud.com.cn/python_sdk.tar.gz
        $ tar zxvf python_sdk.tar.gz
        $ cd ufile-python
        $ sudo python setup.py install

3. Install uai-sdk

        $ sudo sh setup.sh install

4. Install Flask

        $ sudo pip install Flask

5. Install all other lib your inference code required

## How to setup your own http service
1. Write your inference code according to uai API (Please refer to ./uai/README.md
2. Put your code into ./http_server/
3. Now run your http service, the default port is 8080

## UCloud Http Server for UAI
https://github.com/ucloud/uai-sdk-httpserver
