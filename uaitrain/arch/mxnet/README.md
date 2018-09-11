# Intro for UAI Train running MXNet

## Single Node
UAI has following predifined arguments, all applications should follow these args.

    --work_dir=/data/          # Default code dir, UAI platform treat /data/ as the default code path
    --data_dir=/data/data      # Default data dir, UAI platform will map your_data_path into /data/data/
    --output_dir=/data/output  # Default output dir, UAI platform will map your_output_path into /data/output
    --log_dir=/data/output     # Default tensorflow log dir, same as output_dir
    --num_gpus=N               # Num of gpus, this will be decided according to node type 

## Distributed Training
To run maxnet distributed training, we should define following Environments:

        scheduler: master0
        workers: worker0, worker1, worker2, worker3 ....
        ps: ps0, ps1, ps2 ...

The chief node is determined by the 'scheduler'. The other worker nodes are determined by worker list and the ps nodes are determined by ps list. 

UAI Platform follow the classic MXNet distributed training configuration format defined as the running Environments, which will be parsed by KVStore and used by PS-Lite. We will generate the cluster env for each cluster node as:

       DMLC_ROLE='scheduler','server','worker'
       DMLC_PS_ROOT_URI='scheduler_ip'
       DMLC_PS_ROOT_PORT='scheduler_port'
       DMLC_NUM_WORKER='num_workers'
       DMLC_NUM_SERVER='num_servers'
       PS_VERBOSE='1'
       
In UAI Platform, you donot need the lunch.py to start the distributed training. UAI Platform task scheduler will lunch the Parameter Server and Worker for you. Only thing you need to do is to set the --kvstore into dist_xxx such as dist_sync.

