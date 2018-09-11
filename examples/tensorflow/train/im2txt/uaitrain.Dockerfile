From uhub.service.ucloud.cn/uaishare/gpu_uaitrain_ubuntu-16.04_python-2.7_tensorflow-1.7.0:v1.0

RUN pip install -U nltk
CMD python -m nltk.downloader punkt

ADD im2txt /data/im2txt/
ADD ./train.py /data/

