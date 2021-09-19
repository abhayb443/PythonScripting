from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateBatch, ImageFileCreateEntry, Region
from msrest.authentication import ApiKeyCredentials
import time
import os
import cv2


# Replace with valid values
ENDPOINT = "https://customvisionapi-prediction.cognitiveservices.azure.com/"
training_key = "f61487f19efc4e87a08f638836f086b6"
prediction_key = "17b2f44839d14cfd9804f8e13696ad56"
prediction_resource_id = "/subscriptions/9ec6bc74-7dad-4d65-899c-debc882ad33d/resourceGroups/aadhar-grp/providers/Microsoft.CognitiveServices/accounts/customvisionapi"

credentials = ApiKeyCredentials(in_headers={"Training-key": training_key})
trainer = CustomVisionTrainingClient(ENDPOINT, credentials)
prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
predictor = CustomVisionPredictionClient(ENDPOINT, prediction_credentials)

dir = os.path.dirname(__file__)
filename = os.path.join(dir, 'figures/1599247681146752.jpg')
# 1599247681146752.jpg
# cropped-4.hi.jpg

publish_iteration_name  = 'Iteration2'
obj_detection_domain = next(domain for domain in trainer.get_domains() if domain.type == "ObjectDetection" and domain.name == "General")
project = 'customvisionapi-Prediction'
PROJECT_ID = "623023ef-0b24-4799-86e3-0b9c889946f3"

image = 'https://customvisionapi.cognitiveservices.azure.com/customvision/v3.0/Prediction/623023ef-0b24-4799-86e3-0b9c889946f3/detect/iterations/Iteration2/image'
imageurl = 'https://customvisionapi.cognitiveservices.azure.com/customvision/v3.0/Prediction/623023ef-0b24-4799-86e3-0b9c889946f3/detect/iterations/Iteration2/url'

with open(filename, mode="rb") as test_data:
    results = predictor.detect_image(PROJECT_ID, publish_iteration_name, test_data)

# Display the results.
for prediction in results.predictions:
    print(prediction.tag_name, prediction)
    left, top, width, height = prediction.bounding_box.left, prediction.bounding_box.top, prediction.bounding_box.width, prediction.bounding_box.height
    print(left, top, height, width)

# img = cv2.imread(filename)
# crop_img = img[top:left, width:height]
# cv2.imshow("cropped", crop_img)
# cv2.waitKey(0)

    # print(type(prediction))
    # print("\t" + prediction.tag_name +
    #       ": {0:.2f}% bbox.left = {1:.2f}, bbox.top = {2:.2f}, bbox.width = {3:.2f}, "
    #       "bbox.height = {4:.2f}".format(prediction.probability * 100, prediction.bounding_box.left,
    #         prediction.bounding_box.top, prediction.bounding_box.width, prediction.bounding_box.height))

    # left, top, width, height =

"""
Image Rotation to correct Orientation -> Api -> Coordinates -> Cropping -> OCR -> Database   
"""

"""
Address English, Address in multi language, Aadhar Number, Name, Gender, Fathers Name, Date of Birth 
"""

""" Not to be used 
API -> Image -> Text Detection 
"""
