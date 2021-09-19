import tempfile
import os
import cv2
import numpy as np
from PIL import Image
from tesserocr import PyTessBaseAPI
import spacy
from spacy import displacy
import en_core_web_sm
from spacy_langdetect import LanguageDetector


IMAGE_SIZE = 1800
BINARY_THREHOLD = 180

def process_image_for_ocr(file_path):
    # TODO : Implement using opencv
    temp_filename = set_image_dpi(file_path)
    im_new = remove_noise_and_smooth(temp_filename)
    return im_new

def set_image_dpi(file_path):
    im = Image.open(file_path)
    length_x, width_y = im.size
    factor = max(1, int(IMAGE_SIZE / length_x))
    size = factor * length_x, factor * width_y
    # size = (1800, 1800)
    im_resized = im.resize(size, Image.ANTIALIAS)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    temp_filename = temp_file.name
    im_resized.save(temp_filename, dpi=(300, 300))
    return temp_filename

def image_smoothening(img):
    ret1, th1 = cv2.threshold(img, BINARY_THREHOLD, 255, cv2.THRESH_BINARY)
    ret2, th2 = cv2.threshold(th1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    blur = cv2.GaussianBlur(th2, (1, 1), 0)
    ret3, th3 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return th3

def remove_noise_and_smooth(file_name):
    img = cv2.imread(file_name, 0)
    filtered = cv2.adaptiveThreshold(img.astype(np.uint8), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 41,
                                     3)
    kernel = np.ones((1, 1), np.uint8)
    opening = cv2.morphologyEx(filtered, cv2.MORPH_OPEN, kernel)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
    img = image_smoothening(img)
    or_image = cv2.bitwise_or(img, closing)
    return or_image


dir = os.path.dirname(__file__)
filename = os.path.join(dir, 'figures/cropped-4-en.jpg')
res = process_image_for_ocr(filename)

api = PyTessBaseAPI(path='/usr/share/tesseract-ocr/4.00/tessdata/', lang='eng')
try:
    api.SetImageFile(filename)
    data = api.GetUTF8Text()
finally:
    api.End()

nlp = spacy.load("en_core_web_sm")

doc = nlp(data)
print(doc)
#
# # res = displacy.render(doc, style="ent")
#
# nlp.add_pipe(LanguageDetector(), name='language_detector', last=True)
#
# text = """ॊत्ताडैं
#         5/0 ब्रज लाल, ., . . . ,
#         जोबिदोंं, जोंंनिढाड़ोंं फोह्पुर,
#         उत्तर प्रदेश - 2प्र्2635"""
#
# #'This is an english text.'
# doc = nlp(text)
# # document level language detection. Think of it like average language of the document!
# print(doc._.language)
# # sentence level language detection
# for sent in doc.sents:
#    print(sent, sent._.language)


"""
Eng
Address:
$/0 Braj Lal. « jonihan,Jontha,
Fatehpur,
Uttar Pradesh - 212635

Hindi
'ॊत्ताडैं
5/0 ब्रज लाल, ., . . . ,
जोबिदोंं, जोंंनिढाड़ोंं फोह्पुर,
उत्तर प्रदेश - 2प्र्2635
"""
