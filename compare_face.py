import boto3
from boto3.s3.transfer import S3Transfer
# from application.config.Config import *

from botocore.exceptions import ClientError
# import filetype
from PIL import Image
import io
import os


#Amazon Rekognition Key & Secret
Amazon_Rekognition_Key = 'AKIA5X72HLKI6BNWMVPC'
Amazon_Rekognition_Secret = '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'

#Amaon Region
Region = 'ap-south-1'


def image_to_byte_array(image:Image):
    import base64
    with open(image, "rb") as imageFile:
        str = base64.b64encode(imageFile.read())
        # print(str)
        return str


def Compare_Faces(image_1, image_2):
    client = boto3.client('rekognition', aws_access_key_id=Amazon_Rekognition_Key,
                          aws_secret_access_key=Amazon_Rekognition_Secret, region_name=Region)

    Bytes1 = open(image_1, 'rb')
    Bytes2 = open(image_2, 'rb')


    Response = {}
    try:
        response = client.compare_faces(SimilarityThreshold=80, SourceImage={'Bytes': Bytes1.read()},
                                                   TargetImage={'Bytes': Bytes2.read()})

        print(response)

        Bytes1.close()
        Bytes2.close()
        return len(response['FaceMatches']), response['FaceMatches'][0].get('Similarity')

    except Exception as E:

        return E


File_dir = os.path.dirname(__file__)
image1 = os.path.join(File_dir, 'figures/ab_selfie.jpeg')
image2 = os.path.join(File_dir, 'figures/aadhaar_front.jpg')

print(Compare_Faces(image1, image2))

# document reference number : aws object

# Document reference number - 295653873914128
# conf = response['FaceMatches'][0].get('Similarity')                       *
# match = len(response['FaceMatches'])    # 1 - Match     0 - Not Match     *
# category_id                                                               defined
# match-score = response['FaceMatches'][0].get('Similarity')                *
# category_type                                                             defined
# to_be_reviewed                                                            *

# {'SourceImageFace': {'BoundingBox': {'Width': 0.08701442927122116, 'Height': 0.11857196688652039, 'Left': 0.49029675126075745, 'Top': 0.12444198876619339}, 'Confidence': 99.9769515991211}, 'FaceMatches': [{'Similarity': 87.65608215332031, 'Face': {'BoundingBox': {'Width': 0.09652165323495865, 'Height': 0.17960242927074432, 'Left': 0.1521759033203125, 'Top': 0.3389993906021118}, 'Confidence': 99.95227813720703, 'Landmarks': [{'Type': 'eyeLeft', 'X': 0.18129773437976837, 'Y': 0.4072699248790741}, {'Type': 'eyeRight', 'X': 0.22192811965942383, 'Y': 0.40650612115859985}, {'Type': 'mouthLeft', 'X': 0.1859731525182724, 'Y': 0.4783015549182892}, {'Type': 'mouthRight', 'X': 0.21992027759552002, 'Y': 0.4776636064052582}, {'Type': 'nose', 'X': 0.20227572321891785, 'Y': 0.44544512033462524}], 'Pose': {'Roll': -3.279766082763672, 'Yaw': -0.4160781502723694, 'Pitch': 8.453926086425781}, 'Quality': {'Brightness': 38.724586486816406, 'Sharpness': 26.1773681640625}}}], 'UnmatchedFaces': [], 'ResponseMetadata': {'RequestId': 'c7df2df6-8625-432e-a6d4-c2f3e86cc8da', 'HTTPStatusCode': 200, 'HTTPHeaders': {'content-type': 'application/x-amz-json-1.1', 'date': 'Thu, 21 Jan 2021 05:50:14 GMT', 'x-amzn-requestid': 'c7df2df6-8625-432e-a6d4-c2f3e86cc8da', 'content-length': '918', 'connection': 'keep-alive'}, 'RetryAttempts': 0}}
# {"295653873914128": {"conf": 98, "match": "yes", "category_id": 2, "match-score": 95, "category_type": 3, "to_be_reviewed": "no"}}

