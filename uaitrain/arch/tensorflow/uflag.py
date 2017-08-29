'''
UCloud Train basic flags
'''

import tensorflow as tf

flags = tf.app.flags


# =======================================================================
# Constant variables
# --work_dir=/data
# --data_dir=/data/data
# --output_dir=/data/output
#
# Note: Use this params as contant values
#       Do not set this params !!!       
# =======================================================================
'''
	Default work dir. The working dir for the traing job, it will contains:
	    /data/data     --data_dir
	    /data/output   --output_dir
	
	Note: DO NOT CHANGE THIS VALUE
	      UCloud Train Job Executor Will Set it Automatically
'''
flags.DEFINE_string("work_dir", "/data", "Default work path")

'''
	Default data path used in Training, all data will be downloaded into this path
	Please use data in this path as input for Training
	
	Note: DO NOT CHANGE THIS VALUE
	      UCloud Train Job Executor Will Set it Automatically
'''
flags.DEFINE_string("data_dir", "/data/data", "Default data path")

'''
	Default output path used in Training, files in this path will be uploaded to UFile 
	after training finished.
	You can also assume your checkpoint files inside output_path (If you provided 
	in the UCloud console), files will also be downloaded into this path befor 
	Training start

	Note: DO NOT CHANGE THIS VALUE
	      UCloud Train Job Executor Will Set it Automatically
'''
flags.DEFINE_string("output_dir", "/data/output", "Default output path")

'''
	Default tensorboard output path used in Training, iles in this path will be uploaded to UFile 
	after training finished.
	This dir is same as output_dir

	Note: DO NOT CHANGE THIS VALUE
	      UCloud Train Job Executor Will Set it Automatically
'''
flags.DEFINE_string("log_dir", "/data/output/", "Default log path")

'''
	Define num_gpus for training

	Note: DO NOT CHANGE THIS VALUE
	      UCloud Train Job Executor Will Set it Automatically
'''
flags.DEFINE_integer("num_gpus", 0, "Num of avaliable gpus")

# =======================================================================
# Usable variables
# --max_step=<int>
#
# Note: You can SET and USE these params
#       UCloud may use these params as guidance for training projects       
# =======================================================================
'''
	You can use this param to transfer the max_step value

	Note: You can use it as your wish
'''
flags.DEFINE_integer("max_step", 0, "Max Step")
