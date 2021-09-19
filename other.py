from PIL import Image
import pytesseract, re


f = {
     # 'DOB': r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116163975428866.jpg_AadharDateofBirth.jpg',
     # 'Name': r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116163975428866.jpg_AadharName.jpg',
     # 'Num': r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116163975428866.jpg_AadharNumber.jpg',
     # 'SecName': r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116163975428866.jpg_AadharSecondaryName.jpg',
     'DOB' : r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116886748325752.jpg_AadharDateofBirth.jpg',
     'Gen': r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116886748325752.jpg_AadharGender.jpg',
     'Name': r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116886748325752.jpg_AadharName.jpg',
     'Num' : r'/home/abhay/Downloads/Model-Object-Detection/Trained_models/Aadhar_Front/Output/cropped_aadhaar_front_116886748325752.jpg_AadharNumber.jpg',
     }

for i in f:

    t = pytesseract.image_to_string(Image.open(f[i]))
    t = t.strip()
    print(t)

    # if i == 'DOB':
    #     DOB = re.findall(r'(\d{1,4}([.\-/])\d{1,2}([.\-/])\d{1,4})|(\d{1,4})', t, re.IGNORECASE)
    #     print(DOB)
    #
    # elif i == 'GEN':
    #     GEN = re.findall(r'^male$|^female$ |Male$|Female$|m$|M$ |F$|f$', t)
    #     print(GEN)
    #
    # elif i == 'Num':
    #     NUM = re.findall(r'^\w{4}\s\w{4}\s\w{4}$|^\w{14}$', t)
    #     print(NUM)
    #
    # elif i == 'Name' or i == 'Address':
    #     print(t)




"""
string [Name, Father's Name, Mother's Name, Address]
Gender
Date of Birth 
Aadhar Number 
"""
