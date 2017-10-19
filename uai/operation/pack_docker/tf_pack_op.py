import os
from uai.operation.pack_docker.base_pack_op import UaiServicePackOp
from uai.operation.tar.tf_tar_op import UaiServiceTFTarOp

class UaiServiceTFPackOp(UaiServicePackOp, UaiServiceTFTarOp):
    """ Caffe Pack Tool class
    """
    def __init__(self, parser):
        self.platform = 'tensorflow'
        super(UaiServiceTFPackOp, self).__init__(parser)

    def _add_args(self, parser):
        super(UaiServiceTFPackOp, self)._add_args(parser)

    def _parse_args(self):
        super(UaiServiceTFPackOp, self)._parse_args()

