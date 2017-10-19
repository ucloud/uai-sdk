import os
from uai.operation.pack.base_pack_op import UaiServicePackOp
from uai.operation.tar.mxnet_tar_op import UaiServiceMxnetTarOp

class UaiServiceMxnetPackOp(UaiServicePackOp, UaiServiceMxnetTarOp):
    """ Caffe Pack Tool class
    """
    def __init__(self, parser):
        self.platform = 'mxnet'
        self.pack_source = True
        super(UaiServiceMxnetPackOp, self).__init__(parser)

    def _add_args(self, parser):
        super(UaiServiceMxnetPackOp, self)._add_args(parser)

    def _parse_args(self):
        super(UaiServiceMxnetPackOp, self)._parse_args()