from google.cloud import automl
import os
import cv2
import pytesseract
try:
    from PIL import Image
except ImportError:
    import Image
from tesserocr import PyTessBaseAPI
from ocr_service import *
from timeit import timeit


start = timeit()
# Configuration
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/home/abhay/Downloads/gcred.json"
# TODO(developer): Uncomment and set the following variables
project_id = "272292942491"
model_id = "IOD7317797439639912448"

# File Path - Replace by Image Bytes
dir = os.path.dirname(__file__)
file_path = os.path.join(dir, 'figures/1599257934229847.jpg')

# Google Client Initiation
prediction_client = automl.PredictionServiceClient()

# Get the full path of the model.
model_full_id = automl.AutoMlClient.model_path(
    project_id, "us-central1", model_id
)

# Read the file for bytes code
with open(file_path, "rb") as content_file:
    content = content_file.read()

image = automl.Image(image_bytes=content)
payload = automl.ExamplePayload(image=image)

# params is additional domain-specific parameters.
# score_threshold is used to filter the result
# https://cloud.google.com/automl/docs/reference/rpc/google.cloud.automl.v1#predictrequest

params = {"score_threshold": "0.6"}

request = automl.PredictRequest(name=model_full_id,
                                payload=payload,
                                params=params)
response = prediction_client.predict(request=request)

result = []
for index, resp in enumerate(response.payload):
    assert isinstance(resp.display_name, object)
    geodict = {}
    geodict['label'] = resp.display_name
    bounding_box = resp.image_object_detection.bounding_box

    coordinatelist = []
    for ind, vertex in enumerate(bounding_box.normalized_vertices):
        act_vertex = str(vertex)
        act_vertex = act_vertex.replace('x:', '').replace('y:', '').replace('\n', '')
        act_vertex = act_vertex.split(' ')
        act_vertex = [float(i) for i in act_vertex if i]
        coordinatelist.extend(act_vertex)

    geodict[ind] = coordinatelist
    result.append(geodict)

img = cv2.imread(file_path)
height, width = img.shape[:2]

data_payload = []
for res in result:
    ac_x, ac_y, ac_x1, ac_y1 = int(res.get(1)[0] * width), int(res.get(1)[1] * height), \
                               int(res.get(1)[2] * width), int(res.get(1)[3] * height)
    crop_img = img[ac_y:ac_y1, ac_x:ac_x1]
    cv2.imwrite("cropped_{}.jpg".format(res['label']), crop_img)
    # res = process_image_for_ocr("cropped_{}.jpg".format(res['label']))
    # doc = pytesseract.image_to_string(res)
    doc = pytesseract.image_to_string(Image.open("cropped_{}.jpg".format(res['label'])))
    doc = doc.strip().replace('\n', ' ')
    temp_payload = {}
    temp_payload[res['label']]= doc
    data_payload.append(temp_payload)

print(data_payload)
end = timeit()

print("Time Taken - ", end - start)

"""
[
image_object_detection {
  bounding_box {
    normalized_vertices {
      x: 0.09332197159528732
      y: 0.3359321057796478
    }
    normalized_vertices {
      x: 0.5971607565879822
      y: 0.5731649398803711
    }
  }
  score: 0.9959502220153809
}
display_name: "Address"
, 
annotation_spec_id: "587171095069589504"
image_object_detection {
  bounding_box {
    normalized_vertices {
      x: 0.3230959475040436
      y: 0.7367326617240906
    }
    normalized_vertices {
      x: 0.6991687417030334
      y: 0.8395584225654602
    }
  }
  score: 0.9788008332252502
}
display_name: "AadharNumber"
]
"""

"""
[
{'Address': 'WO Amit Kumar Chauraslya, House No 5 324, Block -B. Vinay  Feet f Amamager,  Haryana - 121003'}, 
{'AadharNumber': '5779 6786 9126'}
]
"""
