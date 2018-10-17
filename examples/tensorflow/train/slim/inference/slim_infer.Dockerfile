FROM uhub.service.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-16.04_python-2.7.6_tensorflow-1.6.0:v1.2

EXPOSE 8080
ADD ./slim/. /ai-ucloud-client-django/.
ADD ./sliminfer.py /ai-ucloud-client-django/sliminfer.py
ADD ./slim.conf  /ai-ucloud-client-django/conf.json
ADD ./checkpoint_dir/ /data/output/
ENV UAI_SERVICE_CONFIG /ai-ucloud-client-django/conf.json
CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi

