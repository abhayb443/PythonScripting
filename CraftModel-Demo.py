# import cv2
# import numpy as np
# import os
#
#
# dir = os.path.dirname(__file__)
# filename = os.path.join(dir, 'figures/1599248184789463-lbl.jpg')
#
# bounding_box_image = cv2.imread(filename)
# grayimage = cv2.cvtColor(bounding_box_image, cv2.COLOR_BGR2GRAY)
#
# cv2.imshow('mask', mask)
# cv2.waitKey(0)

# import cv2
# import numpy as np
# from craft_text_detector import Craft
#
# try:
#     from PIL import Image
# except ImportError:
#     import Image
# import pytesseract
#
# img = cv2.imread("/home/abhay/Downloads/Ocr/obj/1599247681146752.jpg")
#
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#
# # cv2.imshow("img", gray)
# # cv2.waitKey(0)
#
# # text = pytesseract.image_to_string(gray)
# # print(text)
#
# # img = cv2.resize(img, None, fx=0.5, fy=0.5)
# # print(img)
#
# # set image path and export folder directory
# image_path = 'figures/1599247681146752-lbl.jpg'
# output_dir = 'outputs/'
#
# # create a craft instance
# craft = Craft(output_dir=output_dir, crop_type="poly", cuda=False)
#
# # apply craft text detection and export detected regions to output directory
# prediction_result = craft.detect_text(image_path)
#
# print(prediction_result)
# # unload models from ram/gpu
# craft.unload_craftnet_model()
# craft.unload_refinenet_model()

import pytesseract
from PIL import Image
import cv2
import numpy as np
import os
from pytesseract import Output


dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'figures/cropped-2.jpg')

im = Image.open(filename)
im.save('ocr.png', dpi=(300, 300))

image = cv2.imread('ocr.png')
image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
retval, threshold = cv2.threshold(image,127,255,cv2.THRESH_BINARY)

text = pytesseract.image_to_string(threshold)

with open("Output.txt", "a", 5, "utf-8") as text_file:
    text_file.write(text)

print(text)


