FROM mkl_uaiservice_ubuntu-14.04_python-2.7.6_intel_caffe-ctpn:v1.0

COPY ctpn_trained_model.caffemodel /ai-ucloud-client-django/models/ctpn_trained_model.caffemodel
COPY ./demo_service.py  /ai-ucloud-client-django/tools/demo_service.py
COPY ./ctpn.conf /ai-ucloud-client-django/ufile.json

EXPOSE 8080

ENV UAI_SERVICE_CONFIG "ufile.json"

CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi
