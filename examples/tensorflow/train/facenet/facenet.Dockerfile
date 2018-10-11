FROM uhub.service.ucloud.cn/uaishare/gpu_uaitrain_ubuntu-16.04_python-3.6_tensorflow-1.7.0:v1.0

COPY code/ /data/
ADD lr-data/ /data/lr-data/