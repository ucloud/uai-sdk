FROM  uhub.service.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-14.04_python-2.7.6_tensorflow-1.4.0:v1.1

EXPOSE 8080
ADD ./wide_deep /ai-ucloud-client-django/
ADD ./wide_deep/conf.json  /ai-ucloud-client-django/conf.json
ENV UAI_SERVICE_CONFIG /ai-ucloud-client-django/conf.json
CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi