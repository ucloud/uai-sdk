FROM uhub.service.ucloud.cn/uaishare/nvidia-cudnn6.0.21-cuda8.0:v1.0

RUN apt-get update
RUN apt-get install -y libprotobuf-dev \
                       libleveldb-dev \
                       libsnappy-dev \
                       libopencv-dev \
                       libhdf5-serial-dev \
                       protobuf-compiler \
                       libgflags-dev \
                       libgoogle-glog-dev \
                       liblmdb-dev \
                       libopenblas-dev

RUN apt-get update

RUN apt-get install -y --no-install-recommends libboost-all-dev libatlas-base-dev libhdf5-dev python-tk \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install numpy cython opencv-python easydict -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com

ADD ./docker_file/py-faster-rcnn/ /root/py-faster-rcnn

RUN cd /root/py-faster-rcnn/caffe-fast-rcnn/python && for req in $(cat requirements.txt); do pip install $req -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com; done

RUN cd /root/py-faster-rcnn/caffe-fast-rcnn/ && make all -j8 && make pycaffe
RUN cd /root/py-faster-rcnn/lib && make

ADD ./docker_file/uai-sdk /uai-sdk
RUN cd /uai-sdk && /usr/bin/python setup.py install

RUN ln -s /dev/null dev/raw1394
ENV PYTHONPATH=/root/py-faster-rcnn/caffe-fast-rcnn/python