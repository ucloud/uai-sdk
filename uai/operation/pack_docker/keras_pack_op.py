import os
from uai.operation.pack_docker.base_pack_op import UaiServicePackOp
from uai.operation.tar.keras_tar_op import UaiServiceKerasTarOp

class UaiServiceKerasPackOp(UaiServicePackOp, UaiServiceKerasTarOp):
    """ Caffe Pack Tool class
    """
    def __init__(self, parser):
        self.platform = 'keras'
        super(UaiServiceKerasPackOp, self).__init__(parser)

    def _add_args(self, parser):
        super(UaiServiceKerasPackOp, self)._add_args(parser)

    def _parse_args(self):
        super(UaiServiceKerasPackOp, self)._parse_args()

