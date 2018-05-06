FROM mkl_uaiservice_ubuntu-14.04_python-2.7.6_intel_caffe-rfcn:v1.0

ADD ./demo_service.py /ai-ucloud-client-django/tools/demo_service.py
ADD ./docker_opt/py-R-FCN/models/pascal_voc/ResNet-101/rfcn_end2end/test_agnostic.prototxt /ai-ucloud-client-django/models/test_agnostic.prototxt
ADD ./rfcn_models/ /ai-ucloud-client-django/models/

COPY ./rfcn.conf /ai-ucloud-client-django/ufile.json

EXPOSE 8080

ENV UAI_SERVICE_CONFIG "ufile.json"

CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi


