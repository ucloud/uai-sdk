From uhub.service.ucloud.cn/uaishare/gpu_uaitrain_ubuntu-16.04_python-2.7_tensorflow-1.7.0:v1.0

RUN pip install tensorflow-hub

ADD ./code/ /data/
