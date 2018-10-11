# Intro for UAI Train running TensorFlow

## Single Node
UAI has following predifined arguments, all applications should follow these args.

    --work_dir=/data/          # Default code dir, UAI platform treat /data/ as the default code path
    --data_dir=/data/data      # Default data dir, UAI platform will map your_data_path into /data/data/
    --output_dir=/data/output  # Default output dir, UAI platform will map your_output_path into /data/output
    --log_dir=/data/output     # Default tensorflow log dir, same as output_dir
    --num_gpus=N               # Num of gpus, this will be decided according to node type 

## Distributed Training
To run tensorflow distributed training, we should define following Environments:

    master: master0
    ps: ps0, ps1, ps2 ...
    worker: worker0, worker1, worker2

The chief worker node is determined by the 'master'. The other worker nodes are determined by worker list and the ps nodes are determined by ps list. 

UAI Platform follow the classic TensorFlow distributed training configuration format defined as the running Environments. It will automatically generate a cluster dict specifiying the dist train cluster config in json format, and set it into env TF\_CONFIG:

	{
      'cluster'     : {
                        'master': ['master-ip:port'],
                        'ps'.   : ['ps-ip0:port', 'ps-ip1:port', 'ps-ip2:port'],
                        'worker': ['worker-ip0:port', 'worker-ip1:port', 'worker-ip2:port']
                      },
      'task'        : {
                        'type' : 'master', 
                        'index': 0
                      },
      'environment' : 'cloud'
    }
    
Task type can also be:
   
        task = {'type': 'ps', 'index': 0}
        task = {'type': 'worker', 'index': 0}

When you are using the Estimator interface, it can automatically recogonize these Env config and start a distributed training.

If you want to write the distributed training code yourself, please parse these os.environ['TF\_CONFIG'] yourself.

Note: estimator.py use its own RunConfig (tensorflow.python.estimator.run\_config) which is differnt from the one tf.contrib.learn.learn\_runner.run use (tensorflow.contrib.learn.python.learn.estimators.run\_config)
 Both will parse the os.environ['TF\_CONFIG'] to get the distributed environment. The estimator.run\_config recogonize both 'master' and 'chief', but learn.estimators.run\_config only recogonize 'master'
