FROM uhub.service.ucloud.cn/uaishare/gpu_uaiservice_ubuntu-16.04_python-2.7.6_tensorflow-1.6.0:v1.0

RUN apt-get update && apt-get install -y --no-install-recommends  python-dev python-tk

RUN pip install shapely typing -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com

EXPOSE 8080
ADD ./code/ /ai-ucloud-client-django/
RUN cd /ai-ucloud-client-django/lanms/&&make
ADD ./east-dist.conf  /ai-ucloud-client-django/conf.json
ENV UAI_SERVICE_CONFIG /ai-ucloud-client-django/conf.json
CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi