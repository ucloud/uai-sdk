FROM uhub.service.ucloud.cn/uaishare/cpu_uaiservice_ubuntu-16.04_python-3.6.2_tensorflow-1.3.0:v1.2
EXPOSE 8080                                                                                                     
ADD ./inference/ /ai-ucloud-client-django/                                                                      
COPY ./CRNN_Tensorflow/crnn_model/ /ai-ucloud-client-django/crnn_model/
COPY ./CRNN_Tensorflow/local_utils/ /ai-ucloud-client-django/local_utils/
COPY ./CRNN_Tensorflow/global_configuration/ /ai-ucloud-client-django/global_configuration/                                              
ADD ./ocr.conf  /ai-ucloud-client-django/conf.json                                                              
ADD ./CRNN_Tensorflow/data/char_dict/ /data/data/                                                               
ENV UAI_SERVICE_CONFIG /ai-ucloud-client-django/conf.json                                                       
CMD cd /ai-ucloud-client-django && gunicorn -c gunicorn.conf.py httpserver.wsgi