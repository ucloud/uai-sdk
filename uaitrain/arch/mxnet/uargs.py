# Copyright 2017 The UAI-SDK Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

def add_uai_args(parser):
    uai = parser.add_argument_group('uai-args', 'the UAI related args')

    '''
        Default work dir. The working dir for the traing job, it will contains:
            /data/data     --data_dir
            /data/output   --output_dir
    
        Note: DO NOT CHANGE THIS VALUE
            UCloud Train Job Executor Will Set it Automatically
    '''
    uai.add_argument('--work_dir', type=str, default="/data", help='Default work path') 

    '''
        Default data path used in Training, all data will be downloaded into this path
        Please use data in this path as input for Training
    
        Note: DO NOT CHANGE THIS VALUE
            UCloud Train Job Executor Will Set it Automatically
    '''
    uai.add_argument("--data_dir", type=str, default="/data/data", help="Default data path")

    '''
        Default output path used in Training, files in this path will be uploaded to UFile 
        after training finished.
        You can also assume your checkpoint files inside output_path (If you provided 
        in the UCloud console), files will also be downloaded into this path befor 
        Training start

        Note: DO NOT CHANGE THIS VALUE
            UCloud Train Job Executor Will Set it Automatically
    '''
    uai.add_argument("--output_dir", type=str, default="/data/output", help="Default output path")

    '''
        Default tensorboard output path used in Training, iles in this path will be uploaded to UFile 
        after training finished.
        This dir is same as output_dir

        Note: DO NOT CHANGE THIS VALUE
            UCloud Train Job Executor Will Set it Automatically
    '''
    uai.add_argument("--log_dir", type=str, default="/data/output", help="Default log path")

    '''
        Define num_gpus for training

        Note: DO NOT CHANGE THIS VALUE
            UCloud Train Job Executor Will Set it Automatically
    '''
    uai.add_argument("--num_gpus", type=int, help="Num of avaliable gpus")

