FROM uhub.service.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-14.04_python-2.7.6_caffe-1.0.0:v1.2

RUN apt-get update
RUN apt-get install -y software-properties-common python-software-properties
RUN add-apt-repository ppa:mc3man/trusty-media
RUN apt-get update
RUN apt-get install -y ffmpeg

COPY uai-sdk /uai-sdk
RUN cd uai-sdk && python setup.py install

EXPOSE 8080
ADD ./code/ /ai-ucloud-client-django/
ADD ./config/caffe_nsfw_video.conf  /ai-ucloud-client-django/conf.json
ENV UAI_SERVICE_CONFIG "/ai-ucloud-client-django/conf.json"
RUN echo "DATA_UPLOAD_MAX_MEMORY_SIZE = 536870912" >> /ai-ucloud-client-django/httpserver/settings.py

CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi