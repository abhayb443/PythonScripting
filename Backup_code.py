import pprint
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
from collections import OrderedDict
import qrtools
import json
import csv
import boto3
from creds import *
from unidecode import unidecode
try:
    from PIL import Image
except ImportError:
    import Image
# import easyocr
# reader = easyocr.Reader(['en'])


Rekognition = boto3.client("textract",
                           aws_access_key_id=Amazon_Rekognition_Key,
                           aws_secret_access_key=Amazon_Rekognition_Secret,region_name='ap-southeast-1')

Rekognition_1 = boto3.client("rekognition",
                           aws_access_key_id=Amazon_Rekognition_Key,
                           aws_secret_access_key=Amazon_Rekognition_Secret,region_name=Region)


def Detect_Text_From_Image(ObjectBytes):
    Response = Rekognition_1.detect_text(Image={'Bytes': ObjectBytes})
    return Response


def Detect_Text_From_Image_Textract(ObjectBytes):
    Response = Rekognition.detect_document_text(Document={'Bytes': ObjectBytes})
    return Response


def files():
    all_lines = []
    # / home / abhay / Downloads / Model - Object - Detection / Trained_models / Aadhar_Back
    with open("/home/abhay/Downloads/Hyerverge_Aadhar_Back/test.txt", "r") as f:
        all_lines = f.read().splitlines()
    return all_lines


def remove_non_ascii(text):
    text = text.encode("ascii", 'ignore')
    text = text.decode()
    text = unidecode(text)
    text = text.replace('\n', '').replace('/s', '').replace('/r', '').replace('/t', '').replace('Address', '')
    text = text.replace('\x0c', '').replace(':', '')
    text = text.strip()
    return text


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

    try:
        image = cv2.imread(imgpath)
        net = cv2.dnn.readNet(
            '/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Back/yolov3_custom_v1_1_final.weights',
            '/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Back/yolov3_custom_v1_1.cfg')

        classes = []
        with open("/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Back/classes.names", "r") as f:
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

        name_dict = {0: 'AadhaarSecondaryAddress', 1: 'AadhaarPrimaryAddress', 2: 'AadhaarQR',
                     3: 'AadhaarNumber', 4: 'AadhaarBarCode'}

        result = {}

        for out in outs:
            res = {}
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
                                directory = '/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Back/Output'

                                if not os.path.isdir(directory):
                                    os.mkdir(directory)

                                cv2.imwrite(os.path.join(directory, "cropped_{}_{}.jpg".format(newpath, name_dict[class_id])),
                                            crop_img)

                                if class_id in [0, 1, 3]:
                                    if not class_id in temp:
                                        success, encoded_image = cv2.imencode('.png', crop_img)
                                        content = encoded_image.tobytes()

                                        # Pytesseract
                                        text = pytesseract.image_to_string(crop_img, lang="eng")
                                        text = remove_non_ascii(text)
                                        if text:
                                            blocks = text
                                        else:
                                            blocks = ''

                                        # Easy Ocr
                                        # text = reader.readtext(crop_img, detail = 0)
                                        # print(text)
                                        # if text:
                                        #     blocks = text
                                        # else:
                                        #     blocks = ''

                                        # Textract
                                        # text = Detect_Text_From_Image_Textract(content)
                                        # try:
                                        #     blocks=text['Blocks'][1]['Text']
                                        # except:
                                        #     blocks = ''

                                        # Rekognition
                                        # text = Detect_Text_From_Image(content)
                                        # if text.get('TextDetections'):
                                        #     blocks = text.get('TextDetections')[0].get('DetectedText')
                                        # else:
                                        #     blocks = ''

                                        label = name_dict[class_id]
                                        res[label] = blocks
                                        temp.append(class_id)

                                elif class_id in [2, 4]:
                                    if not class_id in temp:
                                        response = Barcode_Qrcode_detection(image)
                                        label = name_dict[class_id]
                                        # "Not Readable" if response is None else response
                                        res[label] = response
                                        temp.append(class_id)

                    if res:
                        result.update(res)
                        # cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

                except Exception as e:
                    print(e)

        return result

    except Exception as e:
        print(
            type(e).__name__,  # TypeError
            __file__,  # /tmp/example.py
            e.__traceback__.tb_lineno  # 2
        )


if __name__ == "__main__":
    all = files()
    final = []
    # object = []
    json_object = []

    for i in all:
        final = work_images(i)
        json_object.append(final)
        print(final)

    # Writing to sample.json
    with open("aadhar_back_1.csv", "w") as outfile:
        for i in json_object:
            outfile.write(str(i))
            outfile.write('\n')

    # directory = '/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Not_Found/'
    # if not os.path.isdir(directory):
    #     os.mkdir(directory)
    # imname = imgpath.split('/')
    # path = imname[len(imname) - 1]
    # cv2.imwrite(os.path.join(directory, path), image)

    # Rekognition = boto3.client("textract", aws_access_key_id='AKIAXQ4CJILWH7FRBW4A',
    #                                aws_secret_access_key='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',
    #                                region_name='us-east-1')

    # Rekognition_1 = boto3.client("rekognition", aws_access_key_id='AKIAXQ4CJILWH7FRBW4A',
    #                            aws_secret_access_key='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',
    #                            region_name='us-east-1')

