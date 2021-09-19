import  cv2
import os
import numpy as np
img1= cv2.imread('/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Back/Output/cropped_aadhaar_back_112686473983851.jpg_AadhaarNumber.jpg')
img2=cv2.imread('/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Back/Output/cropped_aadhaar_back_112686473983851.jpg_AadhaarPrimaryAddress.jpg')

# /home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Back/Output/cropped_aadhaar_back_112686473983851.jpg_AadhaarSecondaryAddress.jpg
# images=[]


def vconcat_resize(img_list, interpolation=cv2.INTER_CUBIC):
	# take minimum width
	w_min = min(img.shape[1]for img in img_list)

	# resizing images
	im_list_resize = [cv2.resize(img,
	                             (w_min, int(img.shape[0] * w_min / img.shape[1])),
	                             interpolation=interpolation)
	                  for img in img_list]
	# return final image
	return cv2.vconcat(im_list_resize)

# function calling
img_v_resize = vconcat_resize([img2,img1])

# Writing to sample.json

# img_v_resize = vconcat_resize([img1, img2, img1])
cv2.imwrite('sea_image.jpg', img_v_resize)
