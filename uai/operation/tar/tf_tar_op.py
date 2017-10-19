import os
from uai.operation.tar.base_tar_op import UaiServiceTarOp

class UaiServiceTFTarOp(UaiServiceTarOp):
    """ Caffe Pack Tool class
    """
    def __init__(self, parser):
        super(UaiServiceTFTarOp, self).__init__(parser)

    def _add_args(self, parser):
        super(UaiServiceTFTarOp, self)._add_args(parser)

    def _parse_args(self):
        super(UaiServiceTFTarOp, self)._parse_args()

        self.conf_params['http_server'] = {
            'exec': {
                'main_file': self.main_file,
                'main_class': self.main_class
            },
            'tensorflow': {
                'model_dir': self.model_dir,
            }
        }

    def _get_model_list(self):
        """ TensorFlow specific _get_model_list tool to get model filelist
        """
        model_filelist = os.listdir(os.path.join(self.pack_file_path, self.model_dir))
        for i in model_filelist:
            model_file = os.path.join(self.model_dir, i)
            self.filelist.append(model_file)