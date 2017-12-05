from cfg import Config as cfg
from other import draw_boxes, resize_im, CaffeModel
import cv2, os, caffe, sys
from detectors import TextProposalDetector, TextDetector
import numpy as np

from uai.arch.caffe_model import CaffeAiUcloudModel

NET_DEF_FILE="models/deploy.prototxt"
MODEL_FILE="models/ctpn_trained_model.caffemodel"

class CTPNModel(CaffeAiUcloudModel):
    """ Mnist example model
    """
    def __init__(self, conf):
        super(CTPNModel, self).__init__(conf)

    def load_model(self):
        caffe.set_mode_cpu()
        text_proposals_detector=TextProposalDetector(CaffeModel(NET_DEF_FILE, MODEL_FILE))
        self.text_detector=TextDetector(text_proposals_detector)

    def execute(self, data, batch_size):
        ret = []
        for i in range(batch_size):
            img_array = np.asarray(bytearray(data[i].read()), dtype=np.uint8)
            im = cv2.imdecode(img_array, -1)

            im, f=resize_im(im, cfg.SCALE, cfg.MAX_SCALE)
            text_lines=self.text_detector.detect(im)

            ret_val=str(text_lines) + '\n'
            ret.append(ret_val)
        return ret
