from uai.arch_conf.tf_conf import TFJsonConfLoader

class RetrainJsonConfLoader(TFJsonConfLoader):
    def __init__(self, conf):
        super(RetrainJsonConfLoader, self).__init__(conf)

    def _load(self):
        super(RetrainJsonConfLoader, self)._load()
	self.input_width = eval(self.server_conf['tensorflow']['input_width'])
	self.input_height = eval(self.server_conf['tensorflow']['input_height'])
    
    def get_model_dir(self):
        return self.model_dir

    def get_input_width(self):
    	return self.input_width
		
    def get_input_height(self):
    	return self.input_height
		
