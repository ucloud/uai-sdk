From uhub.service.ucloud.cn/uaishare/gpu_uaitrain_ubuntu-16.04_python-3.6_tensorflow-1.9.0:v1.0 
RUN pip install tqdm
ENV LANG C.UTF-8
ADD ./code/ /data/
