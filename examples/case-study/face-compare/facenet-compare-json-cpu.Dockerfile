FROM uhub.service.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-16.04_python-2.7_tensorflow-1.9.0:v1.2

COPY uai-sdk /uai-sdk
RUN cd uai-sdk && python setup.py install

EXPOSE 8080
ADD ./code/ /ai-ucloud-client-django/
ADD ./facenet-compare-json.conf  /ai-ucloud-client-django/conf.json
ENV UAI_SERVICE_CONFIG /ai-ucloud-client-django/conf.json
CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi