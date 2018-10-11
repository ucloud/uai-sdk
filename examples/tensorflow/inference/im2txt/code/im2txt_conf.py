from uai.arch_conf.tf_conf import TFJsonConfLoader

class Im2txtJsonConfLoader(TFJsonConfLoader):
    def __init__(self, conf):
        super(Im2txtJsonConfLoader, self).__init__(conf)

    def _load(self):
        super(Im2txtJsonConfLoader, self)._load()
        self.input_width = self.server_conf['tensorflow']['input_width']
        self.input_height = self.server_conf['tensorflow']['input_height']
        self.checkpoint = self.server_conf['tensorflow']['checkpoint']
    
	
    def get_model_dir(self):
        return self.model_dir

    def get_input_width(self):
        return self.input_width
		
    def get_input_height(self):
        return self.input_height

    def get_checkpoint(self):
        return self.checkpoint
