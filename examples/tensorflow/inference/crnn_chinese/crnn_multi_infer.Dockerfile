FROM uhub.service.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-16.04_python-3.6_tensorflow-1.9.0:v1.2

EXPOSE 8080
ADD ./inference_multi/ /ai-ucloud-client-django/
ADD ./crnn_multi.conf  /ai-ucloud-client-django/conf.json
ADD ./code/ /data/crnn/
COPY ./data/  /data/data/char_dict/
ENV UAI_SERVICE_CONFIG /ai-ucloud-client-django/conf.json
ENV LANG C.UTF-8
CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi