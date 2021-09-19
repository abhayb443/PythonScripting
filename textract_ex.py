import boto3
from PIL import Image
from creds import *
import cv2
import numpy as np


Rekognition = boto3.client("textract",
                           aws_access_key_id=Amazon_Rekognition_Key,
                           aws_secret_access_key=Amazon_Rekognition_Secret,region_name='ap-southeast-1')

Rekognition_1 = boto3.client("rekognition",
                           aws_access_key_id=Amazon_Rekognition_Key,
                           aws_secret_access_key=Amazon_Rekognition_Secret,region_name=Region)


def image_to_byte_array(image:Image):
    import io
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format="png")
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr

def Detect_Text_From_Image(ObjectBytes):

    Response = Rekognition_1.detect_text(Image={'Bytes': ObjectBytes})
    return Response


def Detect_Text_From_Image_Textract(ObjectBytes):
    Response = Rekognition.detect_document_text(Document={'Bytes': ObjectBytes})
    return Response


# images = [r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116163975428866.jpg_AadharDateofBirth.jpg',
#          r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116163975428866.jpg_AadharName.jpg',
#          r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116163975428866.jpg_AadharNumber.jpg',
#          r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116163975428866.jpg_AadharSecondaryName.jpg',
#          r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116886748325752.jpg_AadharDateofBirth.jpg',
#          r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116886748325752.jpg_AadharGender.jpg',
#          r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116886748325752.jpg_AadharName.jpg',
#          r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116886748325752.jpg_AadharNumber.jpg',
#          ]

def files():
    all_lines = []
    # / home / abhay / Downloads / Hyperverge_Aadhar_Front / test.txt
    with open("/home/abhay/Downloads/Hyperverge_Aadhar_Front/cropped.txt", "r") as f:
        all_lines = f.read().splitlines()

    result = []

    for i in all_lines:
        if 'AadharName.jpg' in i:
            result.append(i)

    return result

images = files()


images = [r'/home/abhay/Downloads/Hyperverge_Aadhar_Front/aadhaar_front_168888749634621.jpg']

json_object = []
final = []

for image in images:
    print(image)
    # im = Image.open(image)
    # le, wi, _ = im.size
    # im_resized = im.resize((200, 200), Image.ANTIALIAS)
    # print(im_resized.size)
    # data = image_to_byte_array(im_resized)

    image = cv2.imread(image)
    h, w, _ = image.shape
    print(h, w, _)

    if h < 100:
        img = cv2.resize(image, None, fx=2, fy=3, interpolation=cv2.INTER_CUBIC)
        h, w, _ = img.shape
        print(h, w, _)

    elif h > 100 & h < 200:
        img = cv2.resize(image, None, fx=1.5, fy=2, interpolation=cv2.INTER_CUBIC)
        h, w, _ = img.shape
        print(h, w, _)

    img = cv2.medianBlur(img, 3)
    img = cv2.bilateralFilter(img, 9, 75, 75)
    success, encoded_image = cv2.imencode('.png', img)
    content = encoded_image.tobytes()

    # text = Detect_Text_From_Image_Textract(data)
    try:
        text = Detect_Text_From_Image(content)
    except Exception as e:
        print(e)

    try:
        print(text)
        print(text.get('TextDetections')[0].get('DetectedText'))
        json_object.append(text)
    except:
        print(text)
        json_object.append(text)

    print()

    # with open("cropped_results.csv", "w") as outfile:
    #     for i in json_object:
    #         outfile.write(str(i))
    #         outfile.write('\n')


    # with open(image, "rb") as image:
    #     # f = image.read()
    # blocks=text['Blocks'][1]['Text']
    # print(blocks)
    # r'/home/abhay/Downloads/Model-Object-Detection/Dataset/aadhaar_front_112356948756634.jpg'
    # [r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116163975428866.jpg_AadharDateofBirth.jpg',
    #  r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116163975428866.jpg_AadharName.jpg',
    #  r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116163975428866.jpg_AadharNumber.jpg',
    #  r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116163975428866.jpg_AadharSecondaryName.jpg',
    #  r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116886748325752.jpg_AadharDateofBirth.jpg',
    #  r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116886748325752.jpg_AadharGender.jpg',
    #  r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116886748325752.jpg_AadharName.jpg',
    #  r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116886748325752.jpg_AadharNumber.jpg',
    #  ]

    # images = [r'/home/abhay/Downloads/Hyperverge_Aadhar_Front/aadhaar_front_269876312512884.jpg']

    # Amaon Region For Textract its Southeast

    # Rekognition = boto3.client("textract", aws_access_key_id='AKIAXQ4CJILWH7FRBW4A',
    #                            aws_secret_access_key='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',
    #                            region_name='us-east-1')
