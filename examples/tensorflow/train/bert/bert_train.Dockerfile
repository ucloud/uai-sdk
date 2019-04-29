FROM uhub.service.ucloud.cn/uaishare/gpu_uaitrain_ubuntu-16.04_python-3.5_tensorflow-1.13.1:v1.0

RUN apt-get install -y locales
RUN locale-gen zh_CN.UTF-8
RUN ln -sfn /usr/local/bin/python /usr/bin/python

ENV LANG C.UTF-8

COPY ./chinese_L-12_H-768_A-12 /data/chinese_L-12_H-768_A-12/
COPY ./bert/ /data/