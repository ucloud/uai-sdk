FROM uhub.service.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-16.04_python-2.7.6_xgboost-0.7:v1.0

EXPOSE 8080
ADD ./binary_classification/ "/ai-ucloud-client-django/"
ENV UAI_SERVICE_CONFIG /ai-ucloud-client-django/xgboost_binary.conf
CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi