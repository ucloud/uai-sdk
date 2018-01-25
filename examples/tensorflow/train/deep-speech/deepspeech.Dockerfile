FROM uhub.ucloud.cn/uaishare/gpu_uaitrain_ubuntu-14.04_python-2.7.6_tensorflow-1.4.0:v1.0

RUN pip install progressbar2 pysftp sox python_speech_features pyxdg bs4 six -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com
RUN pip install paramiko==2.1.1

ADD ./DeepSpeech /data/DeepSpeech
