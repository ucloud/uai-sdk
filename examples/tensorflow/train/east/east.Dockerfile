FROM uhub.service.ucloud.cn/uaishare/gpu_uaitrain_ubuntu-16.04_python-2.7.6_tensorflow-1.5.0:v1.0

RUN apt-get update
RUN apt-get install -y python-opencv python-tk

RUN pip install shapely -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com

ADD ./EAST/ /data/