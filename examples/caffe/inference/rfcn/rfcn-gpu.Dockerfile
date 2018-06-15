FROM uhub.service.ucloud.cn/uaishare/gpu_uaiservice_ubuntu-14.04_python-2.7.6_caffe-py-rfcn:v1.0

EXPOSE 8080

ADD ./rfcn_inference.py /ai-ucloud-client-django/tools/rfcn_inference.py
ADD ./__init__.py /ai-ucloud-client-django/tools/__init__.py
ADD ./rfcn_models/ /ai-ucloud-client-django/models/
COPY ./rfcn.conf /ai-ucloud-client-django/conf.json

RUN cp -fr /root/caffe-py-rfcn/lib /ai-ucloud-client-django/lib/
RUN cp /root/caffe-py-rfcn/tools/_init_paths.py /ai-ucloud-client-django/tools/

ENV UAI_SERVICE_CONFIG "conf.json"

CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi


