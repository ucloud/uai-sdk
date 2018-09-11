# Video/Stream analysis with NSFW
This example shows how to do nsfw check for video and online-streams based on UAI Inference frame work. How to run nsfw for images can be found in examples/caffe/inference/nsfw/README.md.

## Origin
The image pre-process, algorithm, model and original codes are redistributed from another GitHub project in the from of source codes and the codes are modified to adapt to uai-sdk images and structures. Please visit
	https://github.com/yahoo/open_nsfw
for original source. The copyright information is given as below:

Copyright 2016, Yahoo Inc.

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

## Intro
UAI Inference platform provides inference services through HTTP requests. We provide the basic docker images containing django servers which load user-defined inference modules to perform the service. To implement an inference module, you need to implement two methods for the model class: <inference_model>.load\_model() and <inference_model>.execute(). For more details please refer to: 
https://docs.ucloud.cn/ai/uai-inference/guide/principle

In this example, we shows how to build a video and online-streams analysis system using NSFW based on UAI Inference framework. We provide two examples: nsfw for video and nsfw for stream.

## Preparation
Download the current directory into your workplace. A model is given in:
https://github.com/yahoo/open_nsfw/tree/master/nsfw_model. Copy the two files to directory checkpoint_dir/ under code/, and rename them to the same name (for the example below: resnet.caffemodel and resnet.prototxt). You may use any other caffe model with the same procedure.

Put all these files into one directory:

	/data/nsfw/
	|_ code
	|  |_ checkpoint_dir
	|  |  |_ resnet.caffemodel
	|  |  |_ resnet.prototxt
	|  |_ nsfw_inference.py
	|_ nsfw-cpu.Dockerfile
	|_ caffe_nsfw.conf

## UAI Inference Example
We provide two examples:

1. nfs-video: Implemented in nsfw\_video\_inference.py. You can use nsfw-video-cpu.Dockerfile to build a ready-to-use docker image.

2. nfs-stream: Implemented in nsfw\_stream\_inference.py. You can use nsfw-stream-cpu.Dockerfile to build a ready-to-use docker image.

You are free to modify nsfw\_video\_inference.py and nsfw\_stream\_inference.py to fit your scenario.

Note: you should reinstall the uai-sdk into docker (nsfw-video-cpu.Dockerfile, nsfw-stream-cpu.Dockerfile we provided has already add this step) as the official caffe-docker provied by UCloud does not include uai.contrib lib now.