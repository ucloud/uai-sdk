# CRNN Example
This example shows how to run CRNN inference based on UAI Inference Platform.

## 1 Intro
UAI Inference platform can serve inference services through HTTP requests. We provide the basic docker image containing a django server which can load the user-defined inference module to do the service. To implement a inference module, you only need to implement two funcs: load\_model and execute. For more details please refer to https://docs.ucloud.cn/ai/uai-inference/guide/principle.

In this example, we provide two inference service implementations of crnn online inference examples:
1. Inference code for crnn model trained in single-gpu crnn model which is compatable with examples/tensorflow/train/crnn_chinese/code/tools/train_shadownet.py
2. Inference code for crnn model trained in multi-gpu(or distributed training) crnn model which is compatable with examples/tensorflow/train/crnn_chinese/code_multi/tools/train_shadownet_multi.py

## 2 Build CRNN Chinese Inference Service with UAI Inference toolkit
Building a CRNN Chinese inference service docker need some preparations:

1. Write a simple Inference class to load the model, process the data, and run the inference logic.
2. Provide a config file to tell UAI Inference system where to load the model
3. Get the basic UAI Inference docker base image

For more details please refer to https://docs.ucloud.cn/ai/uai-inference/index

## 3. Inference with single-gpu crnn training model
### 3.1 Writing Service Code
We provide the example service code in inference/ocr\_inference.py. We defined ocrModel which derived from TFAiUcloudModel. 

In ocrModel we only need to implement load_model funcs and execute funcs:

1. load_model(self),which loads the given crnn model.
    ``` 
    def load_model(self):
		sess = tf.Session()
		x = tf.placeholder(dtype=tf.float32, shape=[1, 32, 100, 3], name='input')
		'''
		1 define model
		'''
		net=crnn_model.ShadowNet(phase=phase_tensor, hidden_nums=256, layers_nums=2, seq_length=15, num_classes=config.cfg.TRAIN.CLASSES_NUMS, rnn_cell_type='lstm')
		with tf.variable_scope('shadow'):
		   net_out, tensor_dict = net.build_shadownet(inputdata=x)
		decodes, _ = tf.nn.ctc_beam_search_decoder(inputs=net_out, sequence_length=20*np.ones(1), merge_repeated=False)

		sess_config = tf.ConfigProto()
		sess = tf.Session(config=sess_config)
		'''
		2 load model from self.model_dir
		'''
		saver = tf.train.Saver()
		params_file = tf.train.latest_checkpoint(self.model_dir)
		saver.restore(sess=sess, save_path=params_file)
		'''
		3 Register ops into self.output dict.
		  So func execute() can get these ops
		'''
		self.output['sess'] = sess
		self.output['x'] = x
		self.output['y_'] = decodes
    ```

2. execute(self, data, batch_size) which will do the inference. The django server will invoke ocrModel->execute when it receives requests. It will buffer requests into a array named 'data' when possible. In execute(), it first preprocesses the input 'data' array by invoking self.resize_image() for each data[i] and merge all preprocessed images into one batch, then recognize the text. It formats result into list object. (You can format it into json also)
    ```
    	def execute(self, data, batch_size):    
			sess = self.output['sess']
			x = self.output['x']
			y_ = self.output['y_']
			decoder = data_utils.TextFeatureIO()
			ret = []
			for i in range(batch_size):
				'''
				1 load data 
				'''
				image = np.array(Image.open(data[i]))
				image = cv2.cvtColor(np.asarray(image),cv2.COLOR_RGB2BGR)
				image = cv2.resize(image, (100, 32))
				image = np.expand_dims(image, axis=0).astype(np.float32)
				'''
				2 inference
				'''
				preds = sess.run(y_, feed_dict={x: image})
				preds = decoder.writer.sparse_tensor_to_str(preds[0])[0]+'\n'
				ret.append(preds)
               return ret
    ```

### 3.2 Define the Config File
We need to provide the config file ocr.conf to tell the UAI Inference system to get the basic information to load  model. The config file should include following info:

1  "exec" tells which file is used as the entry-point of the user-defined inference logic and which main class is used. <br>
2  "tensorflow" tells which model related info should be parsed by UAI Inference system.

### 3.3 Preparing model
You can use the model you trained on UAI Train Platform. Please following the example in examples/tensorflow/train/crnn_chinese/.

### 3.4 Preparing directory
We put all these files into one directory:
```
|_ code/
|_ data/
|_ inference/
   |_ ocr_inference.py 
   |_ checkpoint_dir/
|_ ocr.conf
|_ ocr.Dockerfile
```
You should put crnn checkpoint files under inference/checkpoint_dir/
### 3.5 Build Your Own Inference Docker
With the above docker file you can now build your own inference docker image.
```
sudo docker build -t uhub.service.ucloud.cn/YOUR_UHUB_REGISTRY/ocr-poem-infer:v1.0 -f ocr.Dockerfile .
```

### 3.6 Run ocr Inference Service 
####  You can run the ocr-inference cpu server Locally as:
```
sudo docker run -it -p 8080:8080 uhub.service.ucloud.cn/YOUR_UHUB_REGISTRY/ocr-poem-infer:v1.0
```

####   Test ocr Inference Service Locally
We provide some images in test_images/
You can test the ocr-inference server as:
```
curl -X POST http://localhost:8080/service -T test_02.jpg
```

## 4. Inference with multi-gpu/dist crnn training model
We provide implementation of inference code compatable with the multi-gpu/dist crnn training example. It takes two steps to build a inference service:
1. export the model checkpoint into a .pb file

2. use .pb file to initialize a inference service

### 4.1 Generating .pb file
We provide inference\_multi/crnn\_multi\_infer.py for you to generate .pb model file (Which is compatable with tfserve). You can run the following command to generate it:

	python crnn_multi_infer.py

Pay attention to the py-modules crnn\_multi\_infer.py required (including basic crnn realted modules such as crnn\_model, local\_utils, etc.), you should put them in the same dir as crnn\_multi\_infer.py. Also you should put the checkpoint files into ./checkpoint\_dir.

The resulting .pb file and the corresponding variables files are located under ./checkpoint\_dir

### 4.1 Writing Service Code
We provide the example service code in inference_multi/crnn_multi\_inference.py. We defined CrnnModel which derived from TFAiUcloudModel. 

In CrnnModel we implement load_model func and execute func:

1. load_model(self), which loads the crnn model by invoking crnn_multi_infer.crnnPredictor('./checkpoint_dir'). We should put the checkpoint files into checkpoint_dir.

2. execute(self, data, batch_size) which will do the inference. The django server will invoke ocrModel->execute when it receives requests. It will buffer requests into a array named 'data' when possible. In execute(), it will call the crnnPredictor to format the images and do the inference call. You can refer to inference\_multi/crnn\_multi\_infer.py for more details. At last, execute() formats result into list object. (You can format it into json also)

### 4.3 Preparing model
You can use the model you trained on UAI Train Platform. Please following the example in examples/tensorflow/train/crnn_chinese/code_multi/.(The multi-gpu version) You should also convert the .ckpt model into .pb model according to [Generating .pb file](#generating-pb-file)

### 4.4 Preparing directory
We put all these files into one directory:
```
|_ code/
|_ data/
|_ inference_multi/
   |_ crnn_multi_inference.py 
   |_ crnn_multi_infer.py 
   |_ checkpoint_dir/
      |_ saved_model.pb
      |_ variables/
|_ crnn_multi.conf
|_ crnn_multi_infer.Dockerfile
```
You should put .pb files under inference\_multi/checkpoint\_dir/

### 4.5 Build Your Own Inference Docker
With the above docker file you can now build your own inference docker image.
```
sudo docker build -t uhub.service.ucloud.cn/YOUR_UHUB_REGISTRY/ocr-poem-infer:v1.0 -f crnn_multi_infer.Dockerfile .
```

### 4.6 Run ocr Inference Service 
####  You can run the crnn-inference cpu server Locally as:
```
sudo docker run -it -p 8080:8080 uhub.service.ucloud.cn/YOUR_UHUB_REGISTRY/ocr-poem-infer:v1.0
```

####   Test ocr Inference Service Locally
We provide some images in test_images/
You can test the crnn-inference server as:
```
curl -X POST http://localhost:8080/service -T test_02.jpg
```

##  Deploy ocr Inference Service into UAI Inference Platform
Please refer to https://docs.ucloud.cn/ai/uai-inference/index for more details. You can directly use the docker image build in [Build](#build-your-own-inference-docker)




