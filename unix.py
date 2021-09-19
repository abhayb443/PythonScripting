import os
import glob
os.system
import PIL
import PIL.Image as Image


d = 0
test_Path = r'/home/abc/Downloads/custom_object_model_23_12/files/back_custom/darknet/Back_Dataset_1/test'

with open((test_Path + '.txt'),'r') as fobj:
	for line in fobj:
		image_List = [[num for num in line.split()] for line in fobj]
		for images in image_List:
			commands = ['./darknet detector test Back_Dataset_1/labelled_data.data cfg/yolov3_custom_v1_1.cfg backup/yolov3_custom_v1_1_final.weights', images[0]]
			os.system(' '.join(commands))
			predicted_image = Image.open("/home/abc/Downloads/custom_object_model_23_12/files/back_custom/darknet/predictions.jpg")
			output = "/home/abc/Downloads/custom_object_model_23_12/files/back_custom/darknet/results/predicted_image%d.jpg"%d
			predicted_image.save(output)
			d+=1


