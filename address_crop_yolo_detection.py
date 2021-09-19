import pprint
# import pandas as pd
import numpy as np
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
import qrtools
import json
import csv
import boto3


Rekognition = boto3.client("textract", aws_access_key_id=Amazon_Rekognition_Key,
                aws_secret_access_key=Amazon_Rekognition_Secret,region_name=Region)

Rekognition_1 = boto3.client("rekognition", aws_access_key_id=Amazon_Rekognition_Key,
                aws_secret_access_key=Amazon_Rekognition_Secret,region_name=Region)


def Detect_Text_From_Image(ObjectBytes):

    Response = Rekognition_1.detect_text(Image={'Bytes': ObjectBytes})

    return Response


def Detect_Text_From_Image_Textract(ObjectBytes):
    Response = Rekognition.detect_document_text(Document={'Bytes': ObjectBytes})
    return Response


def files():
    all_lines = []
    # / home / abhay / Downloads / Hyperverge_Aadhar_Front / test.txt
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

                    Response_Barcode_data['aadhar_number'] = Insert_data['@uid']
                    Response_Barcode_data['full_name'] = Insert_data['@name']
                    Response_Barcode_data['birth_of_year'] = Insert_data['@yob']
                    # Response_Barcode_data['gender']= Insert_data['@gender']
                    Response_Barcode_data['co '] = Insert_data['@co']
                    Response_Barcode_data['city'] = Insert_data['@vtc']
                    Response_Barcode_data['state'] = Insert_data['@state']
                    Response_Barcode_data['district'] = Insert_data['@dist']
                    Response_Barcode_data['pincode'] = Insert_data['@pc']
                    if Insert_data['@gender'] == 'M':
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

    result = {}

    height, width, channel = image.shape

    blob = cv2.dnn.blobFromImage(image, 0.0039, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    for out in outs:
        res = {}
        temp = []

        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > 0.5:
                centre_x = int(detection[0] * width)
                centre_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(centre_x - w / 2)
                y = int(centre_y - h / 2)

                try:
                    crop_img = image[y:y + h, x:x + w]
                    name_dict = {0:'AadharName', 1:'AadharDateofBirth', 2:'AadharGender',
                                 3:'AadharNumber', 4:'AadharQRCode', 5:'AadharProfile',
                                 6:'AadharFatherName', 7:'AadharSecondaryName', 8:'AadharBarcode',
                                 9:'AadharFatherNameSecondary', 10:'AadharContact'}

                    imname = imgpath.split('/')
                    newpath = imname[len(imname) - 1]
                    directory = '/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/'

                    if not os.path.isdir(directory):
                        os.mkdir(directory)

                    cv2.imwrite(os.path.join(directory, "cropped_{}_{}.jpg".format(newpath, name_dict[class_id])),
                                crop_img)
                    # print("Cropped")

                    if class_id in [0, 1, 2, 3, 6]:
                        if not class_id in temp:
                            success, encoded_image = cv2.imencode('.png', crop_img)
                            content = encoded_image.tobytes()

                            # text = Detect_Text_From_Image_Textract(content)
                            # try:
                            #     blocks=text['Blocks'][1]['Text']
                            # except:
                            #     blocks = "Not Readable"

                            text = Detect_Text_From_Image(content)

                            try:
                                blocks = text.get('TextDetections')[0].get('DetectedText')
                            except:
                                blocks = "Not Readable"

                            label = name_dict[class_id]
                            res[label] = blocks
                            temp.append(class_id)

                    elif class_id in [4]:
                        if not class_id in temp:
                            response = Barcode_Qrcode_detection(image)
                            label = name_dict[class_id]
                            res[label] = "Not Readable" if response is None else response
                            temp.append(class_id)
                except:
                    label = newpath
                    res[label] = "Not Detected"

                # cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                if res:
                    result.update(res)
    return result


if __name__ == "__main__":
    all = files()

    final = []
    object = []
    json_object = []

    for i in all:
        final = work_images(i)
        json_object.append(final)

    # Writing to sample.json
    with open("aadhar_front.csv", "w") as outfile:
        for i in json_object:
            outfile.write(str(i))
            outfile.write('\n')

    # directory = '/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Not_Found/'
    # if not os.path.isdir(directory):
    #     os.mkdir(directory)
    # imname = imgpath.split('/')
    # path = imname[len(imname) - 1]
    # cv2.imwrite(os.path.join(directory, path), image)
