FROM uhub.service.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-14.04_python-2.7.6_caffe-1.0.0:v1.2

COPY code/ /ai-ucloud-client-django/
COPY ./mtcnn.conf /ai-ucloud-client-django/ufile.json

EXPOSE 8080

ENV UAI_SERVICE_CONFIG "ufile.json"

CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi