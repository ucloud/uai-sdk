import os
from uai.operation.tar.base_tar_op import UaiServiceTarOp

class UaiServiceMxnetTarOp(UaiServiceTarOp):
    """ Caffe Pack Tool class
    """
    def __init__(self, parser):
        super(UaiServiceMxnetTarOp, self).__init__(parser)

    def _add_args(self, parser):
        super(UaiServiceMxnetTarOp, self)._add_args(parser)
        pack_parser = parser.add_argument_group(
            'Code-Params', 'User Code Storage Info Parameters')
        pack_parser.add_argument(
            '--model_name',
            type=str,
            required=True,
            help='the MXNet model name')
        pack_parser.add_argument(
            '--num_epoch',
            type=int,
            required=True,
            help='the num of the model ckpt epoch')

    def _parse_args(self):
        super(UaiServiceMxnetTarOp, self)._parse_args()
        self.model_name = self.params['model_name']
        self.num_epoch = self.params['num_epoch']
        self.model_prefix = os.path.join(self.model_dir, self.model_name)

        self.conf_params['http_server'] = {
            'exec': {
                'main_file': self.main_file,
                'main_class': self.main_class
            },
            'mxnet': {
                'model_dir': self.model_dir,
                'model_name': self.model_name,
                "num_epoch": self.num_epoch
            }
        }

    def _get_model_list(self):
        """ MXNet specific _get_model_list tool to get model filelist
        """
        self.model_arch_file = self.model_prefix + '-' + 'symbol'+ '.json'
        num_epoch = str(self.num_epoch).zfill(4)
        self.model_weight_file = self.model_prefix + '-' + num_epoch + '.params'
        self.filelist.append(self.model_arch_file)
        self.filelist.append(self.model_weight_file)