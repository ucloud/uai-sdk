FROM uhub.service.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-14.04_python-2.7.6_caffe-1.0.0:v1.2

EXPOSE 8080
ADD ./code/ /ai-ucloud-client-django/
ADD ./caffe_nsfw.conf  /ai-ucloud-client-django/conf.json
ENV UAI_SERVICE_CONFIG "/ai-ucloud-client-django/conf.json"

CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi
