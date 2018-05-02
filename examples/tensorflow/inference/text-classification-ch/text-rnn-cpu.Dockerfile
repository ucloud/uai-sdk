FROM uhub.service.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-16.04_python-2.7.6_tensorflow-1.6.0:v1.0

EXPOSE 8080
ADD ./code/ /ai-ucloud-client-django/
ADD ./txt_class_rnn.conf  /ai-ucloud-client-django/conf.json
ENV UAI_SERVICE_CONFIG /ai-ucloud-client-django/conf.json
CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi