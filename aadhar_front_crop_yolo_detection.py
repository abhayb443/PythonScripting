import pprint
import numpy as np
import pandas as pd
import argparse
import time
import cv2
import os
import pytesseract
import json
import re
from pyzbar.pyzbar import decode
import pyzbar
import qrcode
import xmltodict
from collections import OrderedDict
import qrtools
import json
import csv
import boto3
from creds import *
from unidecode import unidecode
import timeit
try:
    from PIL import Image
except ImportError:
    import Image
import io


def Detect_Text_From_Image(ObjectBytes):
    Rekognition_1 = boto3.client("rekognition",
                                 aws_access_key_id=Amazon_Rekognition_Key,
                                 aws_secret_access_key=Amazon_Rekognition_Secret, region_name=Region)
    Response = Rekognition_1.detect_text(Image={'Bytes': ObjectBytes})
    return Response


def Detect_Text_From_Image_Textract(ObjectBytes):
    Rekognition = boto3.client("textract",
                               aws_access_key_id=Amazon_Rekognition_Key,
                               aws_secret_access_key=Amazon_Rekognition_Secret, region_name='ap-southeast-1')

    Response = Rekognition.detect_document_text(Document={'Bytes': ObjectBytes})
    return Response


def files():
    all_lines = []
    with open("/home/abhay/Downloads/Hyperverge_Aadhar_Front/test.txt", "r") as f:
        all_lines = f.read().splitlines()
    return all_lines


def Barcode_Qrcode_detection(image_bytes):
    Response = {}
    Detector = cv2.QRCodeDetector()  #####detect barcode using detectqrcode
    if Detector is not None:
        for barcode in decode(image_bytes):
            Barcode_decoded_data = barcode.data.decode('utf-8')  ####decoding data from detected barcode data
            ##  frontaadharcard of qrcode name and all data are available

            Response_Barcode_data = {}

            if "name" in Barcode_decoded_data:
                Xml_to_orderdict_data = xmltodict.parse(Barcode_decoded_data,
                                                        encoding='utf-8')  ###convert xml data to orderdict
                Orderdict_to_regDict = dict(OrderedDict(Xml_to_orderdict_data))  ## convert orderdict to regular dict
                ######parse all data into an array#####
                for Insert_data in Orderdict_to_regDict.values():
                    if Insert_data.get('@uid'):
                        Response_Barcode_data['aadhar_number'] = Insert_data['@uid']
                    if Insert_data.get('@name'):
                        Response_Barcode_data['full_name'] = Insert_data['@name']
                    if Insert_data.get('@yob'):
                        Response_Barcode_data['birth_of_year'] = Insert_data['@yob']
                    # Response_Barcode_data['gender']= Insert_data['@gender']
                    if Insert_data.get('@co'):
                        Response_Barcode_data['co '] = Insert_data['@co']
                    if Insert_data.get('@vtc'):
                        Response_Barcode_data['city'] = Insert_data['@vtc']
                    if Insert_data.get('@state'):
                        Response_Barcode_data['state'] = Insert_data['@state']
                    if Insert_data.get('@dist'):
                        Response_Barcode_data['district'] = Insert_data['@dist']
                    if Insert_data.get('@pc'):
                        Response_Barcode_data['pincode'] = Insert_data['@pc']
                    if Insert_data.get('@gender') == 'M':
                        Response_Barcode_data['gender'] = 'male'
                    else:
                        Response_Barcode_data['gender'] = 'female'

                    Response['barcode_data'] = Response_Barcode_data
                    return Response
            else:
                ####for backside barcode aadharnumber detection######
                if re.match(r"(.*)", Barcode_decoded_data,
                            re.MULTILINE):  ####only aadhar number is available in back barcode aadharcard
                    barcode_aadhar_front = re.findall(r"(.*)", Barcode_decoded_data, re.MULTILINE)
                    barcode_aadhar_front = barcode_aadhar_front[0].strip()
                    Response_Barcode_data['Barcode_aadhar_number'] = barcode_aadhar_front

                    Response['Barcode_data'] = Response_Barcode_data
                    return Response
    else:
        return False


def work_images(imgpath):
    # for imgpath in all_lines:
    image = cv2.imread(imgpath)
    assert not isinstance(image, type(None)), 'Image not found'

    net = cv2.dnn.readNet(
        '/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/yolov3_custom_v1_final.weights',
        '/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/yolov3_custom_v1.cfg')

    classes = []
    with open("/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/classes.names", "r") as f:
        classes = f.read().splitlines()

    boxes = []
    confidences = []
    class_ids = []

    layers_names = net.getLayerNames()
    output_layers = [layers_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    height, width, channel = image.shape

    blob = cv2.dnn.blobFromImage(image, 0.0039, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    name_dict = {0: 'AadharName', 1: 'AadharDateofBirth', 2: 'AadharGender',
                 3: 'AadharNumber', 4: 'AadharQRCode', 5: 'AadharProfile',
                 6: 'AadharFatherName', 7: 'AadharSecondaryName', 8: 'AadharBarcode',
                 9: 'AadharFatherNameSecondary', 10: 'AadharContact'}

    result = {}
    result_b = {}

    for out in outs:
        res = {}
        res_b = {}
        temp = []

        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            try:
                if confidence > 0.5:
                    centre_x = int(detection[0] * width)
                    centre_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    x = int(centre_x - w / 2)
                    y = int(centre_y - h / 2)

                    crop_img = image[y:y + h, x:x + w]
                    if crop_img is not None:
                        # cv2.imshow("cropped", crop_img)
                        # cv2.waitKey(0)
                        h, w, _ = crop_img.shape

                        if h != 0 and w != 0:
                            if h < 100:
                                crop_img = cv2.resize(crop_img, None, fx=2, fy=3, interpolation=cv2.INTER_CUBIC)

                            elif h > 100 & h < 200:
                                crop_img = cv2.resize(crop_img, None, fx=1.5, fy=2, interpolation=cv2.INTER_CUBIC)

                            crop_img = cv2.medianBlur(crop_img, 3)
                            crop_img = cv2.bilateralFilter(crop_img, 9, 75, 75)

                            imname = imgpath.split('/')
                            newpath = imname[len(imname) - 1]
                            directory = '/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/'

                            if not os.path.isdir(directory):
                                os.mkdir(directory)

                            cv2.imwrite(os.path.join(directory, "cropped_{}_{}.jpg".format(newpath, name_dict[class_id])),
                                        crop_img)

                            if class_id in [0, 1, 2, 3, 6]:
                                if not class_id in temp:

                                    font = cv2.FONT_HERSHEY_SIMPLEX
                                    # org
                                    org = (0, 25)
                                    # fontScale
                                    fontScale = 1
                                    # Blue color in BGR
                                    color = (0, 0, 0)
                                    # Line thickness of 2 px
                                    thickness = 2
                                    WHITE = [255, 255, 255]
                                    crop_img = cv2.copyMakeBorder(crop_img, 35, 10, 10, 0, cv2.BORDER_CONSTANT,
                                                                  value=WHITE)
                                    """
                                    Before WY - Address
                                    After WY - Aadhaar Number 
                                    """
                                    # Using cv2.putText() method
                                    crop_img = cv2.putText(crop_img, 'WY', org, font, fontScale, color,
                                                           thickness, cv2.LINE_AA)
                                    # cv2.imshow("", crop_img)
                                    # cv2.waitKey(0)

                                    if crop_img.any():
                                        blocks = crop_img
                                    else:
                                        pass

                                    label = name_dict[class_id]
                                    res[label] = blocks
                                    temp.append(class_id)

                            elif class_id in [4]:
                                if not class_id in temp:
                                    response = Barcode_Qrcode_detection(image)
                                    label = name_dict[class_id]
                                    # "Not Readable" if response is None else response
                                    res_b[label] = response
                                    temp.append(class_id)

                if res:
                    result.update(res)
                if res_b:
                    result_b.update(res_b)

            except Exception as e:
                print(e)

    return result, result_b


def pytesseract_ocr(data):
    text = pytesseract.image_to_string(data, lang="eng")
    text = remove_non_ascii(text)
    return text


def textract_ocr(data):
    text = Detect_Text_From_Image_Textract(data)
    return text


def rekognition_ocr(data):
    text = Detect_Text_From_Image(data)
    return text


def easy_ocr(data):
    text = reader.readtext(crop_img, detail = 0)
    return text


def vconcat_resize(img_list, interpolation=cv2.INTER_CUBIC):
    # take minimum width
    w_min = min(img.shape[1] for img in img_list)
    # resizing images
    im_list_resize = [cv2.resize(img, (w_min, int(img.shape[0] * w_min / img.shape[1])),
                                 interpolation=interpolation) for img in img_list]
    # print(type(im_list_resize))

    # return final image
    return cv2.vconcat(im_list_resize)


def get_text(response):
    get_detected_text = []
    get_confidence_primary = []

    for textparser in response['TextDetections']:
        if textparser['Confidence'] < 100 and textparser['Type'] == 'LINE':
            # Push text
            get_detected_text.append(textparser['DetectedText'])
            # Push corresponding confidence
            # get_confidence_primary.append(textparser['Confidence'])

    return get_detected_text


def writer_func(data):
    # Writing to sample.json
    with open("aadhar_front.csv", "w") as outfile:
        for i in json_object:
            outfile.write(str(i))
            outfile.write('\n')


def main_pg():
    all = files()
    final = []

    for i in all:
        final, qr_br = work_images(i)

        img_list = [i for i in final.values() if i is not None]
        img = vconcat_resize(img_list)

        success, encoded_image = cv2.imencode('.png', img)
        cv2.imshow('File ', encoded_image)
        content = encoded_image.tobytes()

        print(type(content))

        nparr = np.fromstring(content, np.uint8)

        img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        cv2.imshow("File", img_np)

        response = rekognition_ocr(content)
        result = get_text(response)
        print(result)
        Aadhar_address = {}
        Aadhar_number = {}
        output = {}

        if len(result) > 2:
            ind_pos = result.index("WY", 1)

            Aadhar_address = result[1:ind_pos]
            Aadhar_address = ' '.join([str(elem) for elem in Aadhar_address])
            output['Aadhar_address'] = Aadhar_address

            Aadhar_number = result[ind_pos + 1]
            output['Aadhar_number'] = Aadhar_number

        else:
            output = {'Text': result[1]}

        output.update(qr_br)
        print(output)

    return output


if __name__ == "__main__":

    start = timeit.timeit()
    main_pg()
    end = timeit.timeit()
    print(end-start)
