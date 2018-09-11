# MPI Wrapper for MXNet Dist Train
We provide mpi\_wrapper.py for users want to run distributed training based on MPI. You do not need to config all nodes and use launch.py provided by original MXNet to run the MXNet Distributed training job. 

UAI Train platform automatically config the GPU nodes for you and launch worker/ps tasks on each node for you. (Please see https://docs.ucloud.cn/ai/uai-train/dist/mxnet for more detail) For MPI tasks, in order to run job with **mpirun**, we provide mpi\_wrapper.py to help you to run job with mpi env. So the entrypoint for your task in UAI Train should be mpi\_wrapper.py. We can run a dist job as:

	/data/mpi_wrapper.py --command="python /data/train_imagenet.py --batch-size=128 --num-layers=50  --image-shape=3,299,299 --num-epochs=1 --kv-store=dist_sync --data-train=/data/data/train-rec --data-val=/data/data/val-rec --data-nthreads=8"
	
mpi\_wrapper.py accepts only one argument **command** as the actual entrypoint of your program, e.g., **python /data/train\_imagenet.py**. all following args will be attached to your entrypoint. It also provides an extra argument as --uai-hosts=ip1,ip2,ip3,ip4 that you can get all hosts in the cluster.