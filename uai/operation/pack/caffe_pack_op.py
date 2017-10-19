import os
from uai.operation.pack.base_pack_op import UaiServicePackOp
from uai.operation.tar.caffe_tar_op import UaiServiceCaffeTarOp

class UaiServiceCaffePackOp(UaiServicePackOp, UaiServiceCaffeTarOp):
    """ Caffe Pack Tool class
    """
    def __init__(self, parser):
        self.platform = 'caffe'
        self.pack_source = True
        super(UaiServiceCaffePackOp, self).__init__(parser)

    def _add_args(self, parser):
        super(UaiServiceCaffePackOp, self)._add_args(parser)

    def _parse_args(self):
        super(UaiServiceCaffePackOp, self)._parse_args()

