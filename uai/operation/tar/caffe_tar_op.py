import os
from uai.operation.tar.base_tar_op import UaiServiceTarOp

class UaiServiceCaffeTarOp(UaiServiceTarOp):
    """ Caffe Pack Tool class
    """
    def __init__(self, parser):
        super(UaiServiceCaffeTarOp, self).__init__(parser)

    def _add_args(self, parser):
        super(UaiServiceCaffeTarOp, self)._add_args(parser)
        code_parse = parser.add_argument_group(
            'Code-Params', 'User Code Storage Info Parameters')
        code_parse.add_argument(
            '--model_name',
            type=str,
            required=True,
            help='the Caffe model name')

    def _parse_args(self):
        super(UaiServiceCaffeTarOp, self)._parse_args()
        self.model_name = self.params['model_name']

        self.conf_params['http_server'] = {
            'exec': {
                'main_file': self.main_file,
                'main_class': self.main_class
            },
            'caffe': {
                'model_dir': self.model_dir,
                'model_name': self.model_name
            }
        }

    def _get_model_list(self):
        """ Caffe specific _get_model_list tool to get model filelist
        """
        self.model_arch_file = os.path.join(self.model_dir, self.model_name + '.prototxt')
        self.model_weight_file = os.path.join(self.model_dir, self.model_name + '.caffemodel')
        self.filelist.append(self.model_arch_file)
        self.filelist.append(self.model_weight_file)