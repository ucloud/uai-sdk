# cifar10_simple Example
This example show how to run cifar10 inference based on UAI Inference Platform.

## 1 Intro
UAI Inference platform can serve inference services through HTTP requests. 
We provide the basic docker image containing a django server which can load the user-defined inference module to do the service. 
To implement a inference module, you only need to implement two funcs: load\_model and execute. 
For more details please refer to https://docs.ucloud.cn/ai/uai-inference/guide/principle.

In this example, we provide the inference service example: cifarModel which accepts one picture and gives picture category.

## 2 Build cifar Inference Service with UAI Inference toolkit
Building a cifar inference service docker need some preparations:

1. Write a simple Inference class to load the model, process the data, and run the inference logic.
2. Provide a config file to tell UAI Inference system where to load the model.
3. Get the basic UAI Inference docker base image.

For more details please refer to https://docs.ucloud.cn/ai/uai-inference/index

### 2.1 Writing Service Code
We provide the example service code in cifar_infer.py. We defined cifarModel which derived from TFAiUcloudModel. 

In cifarModel we only need to implement load_model funcs and execute funcs:

1. load_model(self),which loads the given model.
    ``` 
    def load_model(self):
		sess = tf.Session()
		x = tf.placeholder(dtype=tf.float32, shape=[1, 24, 24, 3], name='input')
		#inferece
		pred = tf.argmax(cifar10.inference(x),axis=1)
            #load model
		saver = tf.train.Saver()
		params_file = tf.train.latest_checkpoint(self.model_dir)
		saver.restore(sess=sess, save_path=params_file)
		#Register ops into self.output dict.So func execute() can get these ops
		self.output['sess'] = sess
		self.output['x'] = x
		self.output['y_'] = pred

    ```
2. execute(self, data, batch_size) which will do the inference. 
The django server will invoke cifarModel->execute when it receives requests. 
It will buffer requests into a array named 'data' when possible. In execute(), 
it first preprocesses the input 'data' array by invoking self.resize_image() for each data[i] and merge all preprocessed images into one batch, 
then recognize the text. It formats result into list object. (You can format it into json also)
    ```
    	def execute(self, data, batch_size):	
			sess = self.output['sess']
			x = self.output['x']
			y_ = self.output['y_']
			ret = []
			for i in range(batch_size):
                            '''
    			1 load data 
    			'''
				image = Image.open(data[i])
				image = cv2.cvtColor(np.asarray(image),cv2.COLOR_RGB2BGR)
				image = cv2.resize(image, (24, 24))
				mean=np.mean(image)
				std=np.std(image)
				image=(image-mean)/max(std,1/np.sqrt(image.size))
				image = np.expand_dims(image, axis=0).astype(np.float32)
				'''
    			2 inference
    			'''
				preds = sess.run(y_, feed_dict={x: image})
				pred_label=label_dict[preds[0]]
				ret.append(pred_label)
			return ret
    ```

### 2.2 Define the Config File
We need to provide the config file to tell the UAI Inference system to get the basic information to load  model. 
The config file should include following info:

1  "exec" tells which file is used as the entry-point of the user-defined inference logic and which main class is used. <br>
2  "tensorflow" tells which model related info should be parsed by UAI Inference system.



## 3 Preparing model
You can use the model you trained on UAI Train Platform. You can also download it according to checkpoint_dir/intro.txt
## 4 Preparing directory
We put all these files into one directory:
```
|_ code/
|_ inference/
   |_ cifar_inference.py 
   |_ checkpoint_dir/
|_ cifar.conf
|_ cifar_infer.Dockerfile
```
## 5 Build Your Own Inference Docker
With the above docker file we can now build your own inference docker image.

```
sudo docker build -t uhub.service.ucloud.cn/YOUR_UHUB_REGISTRY/cifar_simple-infer:v1.0 -f cifar_infer.Dockerfile .
```


## 6 Run cifar Inference Service 
###  You can run the cifar_simple-inference  server Locally as:
```
sudo docker run -it -p 8080:8080 uhub.service.ucloud.cn/YOUR_UHUB_REGISTRY/cifar_simple-infer:v1.0 
```
###   Test cifar Inference Service Locally
We provide some images in test_images,
You can test the cifar_simple-inference server as:
```
curl -X POST http://localhost:8080/service -T deer.png
```
###  Deploy cifar Inference Service into UAI Inference Platform
Please refer to https://docs.ucloud.cn/ai/uai-inference/index for more details. 
You can directly use the docker image build in [Build](#build-your-own-inference-docker)




