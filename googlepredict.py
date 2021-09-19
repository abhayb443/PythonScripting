from google.cloud import automl
import os
import cv2
import pytesseract
try:
    from PIL import Image
except ImportError:
    import Image

from ocr_service import *
from timeit import timeit
from ocr_service import set_image_dpi, image_smoothening, remove_noise_and_smooth

def google_ocr():
    start = timeit()
    # Configuration - gcred.json
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/abhay/Downloads/my_gcp_cred.json"
    project_id = "big-crow-298110"
    model_id = "IOD6838304816813309952"

    # File Path - Replace by Image Bytes
    File_dir = os.path.dirname(__file__)
    file_path = os.path.join(File_dir, 'TestData/LOS1381524516386L57Q_POA.jpg') # LOS1381524516386L57Q_POA.jpg

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

    if response.payload:
        for index, resp in enumerate(response.payload):
            assert isinstance(resp.display_name, object)
            geodict = {'label': resp.display_name}
            bounding_box = resp.image_object_detection.bounding_box

            coordinatelist = []
            for vertex in bounding_box.normalized_vertices:
                act_vertex = str(vertex)
                act_vertex = act_vertex.replace('x:', '').replace('y:', '').replace('\n', '')
                act_vertex = act_vertex.split(' ')
                act_vertex = [float(i) for i in act_vertex if i]
                coordinatelist.extend(act_vertex)

            # geodict[ind] = coordinatelist # enumerate removed from vertex loop
            geodict[index] = coordinatelist
            result.append(geodict)

        img = cv2.imread(file_path)
        height, width = img.shape[:2]

        data_payload = []
        for index, res in enumerate(result):
            ac_x, ac_y, ac_x1, ac_y1 = int(res.get(index)[0] * width), int(res.get(index)[1] * height), \
                                       int(res.get(index)[2] * width), int(res.get(index)[3] * height)
            crop_img = img[ac_y:ac_y1, ac_x:ac_x1]
            cv2.imwrite("cropped_{}.jpg".format(res['label']), crop_img)

            # src = cv2.imread("cropped_{}.jpg".format(res['label']), cv2.IMREAD_UNCHANGED)
            # scale_percent = 20
            # width = int(src.shape[1] * scale_percent / 100)
            # height = int(src.shape[0] * scale_percent / 100)
            # # dsize
            # dsize = (width, height)
            # # resize image
            # output = cv2.resize(src, dsize)
            # cv2.imwrite("cropped_{}.jpg".format(res['label']), output)

            # set_image_dpi("cropped_{}.jpg".format(res['label']))
            # remove_noise_and_smooth("cropped_{}.jpg".format(res['label']))

            doc = pytesseract.image_to_string(Image.open("cropped_{}.jpg".format(res['label'])), lang='eng+Hin')
            doc = doc.strip().replace('\n', ' ')
            temp_payload = {res['label']: doc}
            data_payload.append(temp_payload)

        final_res = data_payload

    else:
        final_res = "Sorry, no object detected, Please provide a better crisp image. Thanks - Kissht"

    end = timeit()
    print("Time Taken - ",end - start)
    return final_res


print(google_ocr())

# Project Id - 272292942491
# Model - 1 Iteration IOD7317797439639912448
# Model - 2 Iteration IOD5836253899723374592

# 1599259224611258.jpg
# 1599258889856475.jpg
# 1599259897471375.jpg

# 1599257828868697.jpg
# 1599248995669158.jpg
# LOS1358187433964S86P_POA.jpg

# LOS1381524516386L57Q_POA.jpg
# LOS1381512851748XNJW_POA.jpg
# LOS1358146327589H2CG_POA_CROP.jpg
# LOS1358162746544CGIF_POA.jpg

# LOS1135816146235GBEY_POI.png
# LOS1158334383587AK3G_POA.jpg  No Object Detected here
# 1599257934229847.jpg
# 1995312599586715.jpg  Barcode

