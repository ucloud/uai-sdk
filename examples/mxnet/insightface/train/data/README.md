# Build MXNet Dataset
Here we show how to setup a self-defined dataset for insightface/ArcFace training. Basically, it has 2 steps todo:

1. Align the faces one by one and generate the landmark info for each image.
2. Pack the images into MXNet *.rec file

## Aligned Faces and Generate Landmark File
We provide dir2lmk.py to do face image preprocessing (aligning faces using MTCNN) and generate landmark info for each image. The resulting landmark file will contains 12 entries:

	1: file path
	2: face_id
	3~12: lamdmark value

### dir2lmk.py
dir2lmk.py takes following params:

	--origin_dir  The directory containing the original images
	--data_dir    The directory containing the aligned(preprocessed) images
	--lmk_file    The file to store the landmark info
	--dir_prefix  The dir-prefix attach to each face_id. The dir2lmk.py will generate one subdir for each face_id under 'data_dir'. (e.g., the face_id is 0, and dir_prefix is 'u.', the resulting subdir will be named u.0/)
	--start_id    The starting face_id, the default value is 0.
	--mtcnn_path  MTCNN model path

dir2lmk.py will do the following steps to process the provided dataset:

1. Iterate the **origin\_dir** and read images one by one.
2. Use MTCNN to detect the face location as well as the landmark info of each image.
3. preprocess the faces detected in Step 2 and save the image into **data\_dir**.
4. write the landmark info into **lmk\_file**

### Process Images and Generate Landmark File
#### Preparing code for processing images
You should follow https://github.com/deepinsight/insightface to download the insightface code and put dir2lmk.py into the src/data/, for example:

    /example/insightface/code/
    |_ src/
    |  |_ train_softmax.py
    |  |_ data.py
    |  |_ data/
    |  |  |_ dir2lmk.py
    |  |  |_ dir2rec.py
    |  |  |_ glint2lst.py
    |  |  |_ ...
    |  |_ align/
    |  |_ common/
    |  |_ ...
    |  |_ utils/
    |_ ...

#### Preparing Your Original Images
You should prepare your own dataset (images of human face) first. The data should organized as follows:

	/PATH_TO_ORIGINAL_DATASET/
	|_ face_data/
	|  |_ name1/
	|  |  |_ name1_1.jpg
	|  |  |_ name1_2.jpg
	|  |_ name2/
	|  |  |_ name1_1.jpg
	|  |  |_ name1_2.jpg
	|  |  |_ ...
	|  |  |_ name1_N.jpg
	|  |_ name3/
	|  |  |_ name1_1.jpg
	|  |  |_ name1_2.jpg
	|  |  |_ name1_3.jpg
	|  |_ name4/
	...
	|  |_ nameN/
	
Each seperate **Human sub dir** should have at least 2 images.

#### Use dir2lmk.py to Align the Images and Generate Landmark File
You can use the following CMDs to generate aligned images and landmark file:

	python src/data/dir2lmk.py --origin_dir /PATH_TO_ORIGINAL_DATASET/face_data/ --data_dir /PATH_TO_ALIGNED_DATA/face_aligned/ --lmk_file ./aligned_lmk.txt --dir_prefix 'face2019_'  --mtcnn_path /data/deploy/mtcnn-model/
	
The command will generate aligned face images into /PATH\_TO\_ALIGNED\_DATA/face\_aligned/ as follows:

	/PATH_TO_ALIGNED_DATA/
	|_ face_aligned/
	|  |_ face2019_0/
	|  |  |_ xxx.jpg
	|  |  |_ xxx.jpg
	|  |_ face2019_1/
	|  |  |_ xxx.jpg
	|  |  |_ ...
	|  |  |_ xxx.jpg
	|  |_ face2019_3/
	|  |  |_ xxx.jpg
	|  |  |_ xxx.jpg
	|  |  |_ xxx.jpg
	|  |_ face2019_4/
	...
	|  |_ face2019_N/
	
It will also generate a aligned\_lmk.txt.

**Note: If the face from the original dataset cannot be aligned, it will be deprecated**

#### Generate label.txt from Landmark File
You can use glint2lst.py to generate label.txt using following CMD:

	python src/data/glint2lst.py ./ aligned > /PATH_TO_ALIGNED_DATA/face_aligned/label.txt
	
The first param is where the landmark file (e.g., aligned\_lmk.txt is stored). The second param is the name prefix of the landmark file (e.g., aligned).

### Build Rec file
You can use original dir2rec.py to build the single rec file for training, using the following CMD:

	python src/data/dir2rec.py --input /PATH_TO_ALIGNED_DATA/face_aligned/ --output /PATH_TO_REC_FILE/face_rec/
	cp PATH_TO_ALIGNED_DATA/face_aligned/label.txt /PATH_TO_REC_FILE/face_rec/train.lst
	
It will generate the train.rec, train.idx and property from aligned images and the label.txt. As the training method also need the train.lst which is same as label.txt, we copy it into the same dir as train.rec.

### Other Data Used by Insightface
You should also download the test dataset used in the evaluation steps in training. They are agedb\_30.bin, cfp\_fp.bin, lfw.bin you can download them from https://github.com/deepinsight/insightface/wiki/Dataset-Zoo (MS1M), and put them into /PATH\_TO\_REC\_FILE/face\_rec/.  Now the face\_rect contains following data:

	/PATH_TO_REC_FILE/face_rec/
	|_ agedb_30.bin
	|_ cfp_fp.bin
	|_ lfw.bin
	|_ property
	|_ train.idx
	|_ train.lst
	|_ train.rec
	
Now you can train your own face-reco model using you own dataset.

## Build Rec chucks
TODO
