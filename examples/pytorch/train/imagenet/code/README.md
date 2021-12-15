### 使用流程
1. 上传docker镜像至Uhub
2. 上传数据至文件存储ufs或对象存储us3中
3. 创建分布式训练任务

### 调用方式
UAI-Train平台为用户作业注入了启动分布式训练所需的环境变量，结合这些环境变量，通过PyTorch官方提供的torch.distributed.launch或者torch.multiprocessing启动分布式训练作业。

#### 关键参数
* --**work_dir**，默认值/data
* --**data_dir**，外部存储挂载进容器中的输入目录，默认值/data/data
* --**output_dir**，外部存储挂载进容器中的输出目录，默认值/data/output
* --**num_gpus**，当前节点的GPU数量
 
#### 环境变量
* **MASTER_ADDR**：master的地址（即RANK=0的worker）
* **MASTER_PORT**：master的端口（即RANK=0的worker）
* **RANK**：当前节点的编号，不同节点编号不同
* **WORKER_NUM**：训练节点数量
* **WORKER_GPU_NUM**：单个节点包含GPU数量

#### 启动训练
使用如下命令启动DDP分布式训练任务：
```
-m torch.distributed.launch --use_env --nproc_per_node $WORKER_GPU_NUM --master_addr $MASTER_ADDR --node_rank $RANK --master_port $MASTER_PORT --nnodes=$WORKER_NUM <代码文件的绝对路径及参数>

注：UAI-Train平台默认使用python执行，故cmd这里不需要显式添加python指令
```

关于torch.distributed.launch的更多信息可参见官网或[代码文件](https://github.com/pytorch/pytorch/blob/fc8404b5bc7e9721aa93021cdc27de818df64d8d/torch/distributed/launch.py)
