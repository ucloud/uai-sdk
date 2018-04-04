FROM uhub.service.ucloud.cn/uaishare/gpu_uaitrain_ubuntu-16.04_python-2.7.6_caffe2-detectron:v1.0

COPY dataset_catalog.py /data/detectron/lib/datasets/dataset_catalog.py
COPY weights/ /data/weights/
COPY conf/ /data/conf/