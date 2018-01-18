From uhub.service.ucloud.cn/uaishare/gpu_uaitrain_ubuntu-14.04_python-2.7.6_tensorflow-1.4.0:v1.0

RUN apt-get update 
RUN apt-get install python-tk -y

ADD ./research /data/

RUN cd /data/ && python setup.py install && cd slim && python setup.py install
