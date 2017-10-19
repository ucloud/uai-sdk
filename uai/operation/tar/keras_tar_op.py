import os
from uai.operation.tar.base_tar_op import UaiServiceTarOp

class UaiServiceKerasTarOp(UaiServiceTarOp):
    """ Caffe Pack Tool class
    """
    def __init__(self, parser):
        super(UaiServiceKerasTarOp, self).__init__(parser)

    def _add_args(self, parser):
        super(UaiServiceKerasTarOp, self)._add_args(parser)
        code_parse = parser.add_argument_group(
            'Code-Params', 'User Code Storage Info Parameters')
        code_parse.add_argument(
            '--model_name',
            type=str,
            required=True,
            help='the Keras model name')
        code_parse.add_argument(
            '--all_one_file',
            type=str,
            required=False,
            default='false',
            choices=['true', 'false'],
            help='whether the model is all in one file, default is false')
        code_parse.add_argument(
            '--model_arch_type',
            type=str,
            default='json',
            help='the model arch type to save')

    def _parse_args(self):
        super(UaiServiceKerasTarOp, self)._parse_args()
        self.model_name = self.params['model_name']
        self.all_one_file = True if self.params['all_one_file'] == 'true' else False
        self.model_arch_type = self.params['model_arch_type']

        self.conf_params['http_server'] = {
            'exec': {
                'main_file': self.main_file,
                'main_class': self.main_class
            },
            'keras': {
                'model_dir': self.model_dir,
                'model_name': self.model_name,
                "all_one_file": self.all_one_file,
                "model_arch_type": self.model_arch_type
            }
        }

    def _get_model_list(self):
        """ Keras specific _get_model_list tool to get model filelist
        """
        if not self.all_one_file:
            self.model_arch_file = os.path.join(self.model_dir,
                                               self.model_name + '.' + self.model_arch_type)
            self.model_weight_file = os.path.join(self.model_dir, self.model_name + '.h5')
            self.filelist.append(self.model_arch_file)
            self.filelist.append(self.model_weight_file)
        else:
            self.model_file = os.path.join(self.model_dir, self.model_name + '.h5')
            self.filelist.append(self.model_file)