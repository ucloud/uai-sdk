# Build MXNet Dataset

## Format of Lamdmark File and Aligned Faces
Each link of Lamdmark file contains one landmark info for one example, it should contain 12 entries:

	1: file path
	2: face_id
	3~12: lamdmark value

dir2lmk.py provides methods to generate landmark file as well as aligned faces images for arbitrary face-img data.

## Build Rec file
You can use original dir2rec.py to build the single rec file for training

## Build Rec chucks
TODO
