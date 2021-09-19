import boto3


def Detect_Text_From_Image_Textract(ObjectBytes):
    # Amaon Region For Textract its Southeast

    Rekognition = boto3.client("textract", aws_access_key_id='AKIAXQ4CJILWH7FRBW4A',
                               aws_secret_access_key='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',
                               region_name='us-east-1')

    Response = Rekognition.detect_document_text(Document={'Bytes': ObjectBytes})

    return Response


images = [r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116163975428866.jpg_AadharDateofBirth.jpg',
 r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116163975428866.jpg_AadharName.jpg',
 r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116163975428866.jpg_AadharNumber.jpg',
 r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116163975428866.jpg_AadharSecondaryName.jpg',
 r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116886748325752.jpg_AadharDateofBirth.jpg',
 r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116886748325752.jpg_AadharGender.jpg',
 r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116886748325752.jpg_AadharName.jpg',
 r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116886748325752.jpg_AadharNumber.jpg',
 ]

for image in images:
    with open(image, "rb") as image:
      f = image.read()

    text = Detect_Text_From_Image_Textract(f)
    try:
        blocks=text['Blocks'][1]['Text']
        print(blocks)
    except:
        print(text['Blocks'])

# for i in blocks:
#     print(i)
