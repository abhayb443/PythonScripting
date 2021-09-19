import cv2
import os
import numpy as np

dir = os.path.dirname(__file__)
file_path = os.path.join(dir, 'figures/1599257934229847.jpg')

img = cv2.imread(file_path)
# print(img.shape)
height, width = img.shape[:2]

x= 0.3230959475040436
y= 0.7367326617240906
x1= 0.6991687417030334
y1= 0.8395584225654602

ac_x = int(x * width)
ac_y = int(y * height)
ac_x1 = int(x1 * width)
ac_y1 = int(y1 * height)

# print(ac_x, ac_y, ac_x1, ac_y1)

# new_x = x* 1000
# new_x1 = x1 * 1000
# new_y = y * 1000
# new_y1 = y1 * 1000

# img = cv2.imread(file_path,cv2.IMREAD_COLOR)
# start_point = ac_x
# end_point = ac_y
# color = (0, 20, 200)
# window_name = 'Image'

crop_img = img[ac_y:ac_y1, ac_x:ac_x1]

"""Img Show"""
cv2.imshow('Img', crop_img)
cv2.waitKey(0)


"""Create Rectangle"""
# image = cv2.rectangle(img, (ac_x, ac_y), (ac_x1, ac_y1), color, thickness=1)
# cv2.imshow('Img', image)
# cv2.waitKey(0)
