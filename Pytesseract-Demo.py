import os

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
from timeit import timeit


starttime = timeit()
dir = os.path.dirname(__file__)
filename = os.path.join(dir, 'figures/cropped-4-en.jpg')
data = pytesseract.image_to_string(Image.open(filename))
data = str(data).strip().replace('\n', ' ')
print(data)

endtime = timeit()
print("Time Taken - ",endtime - starttime)

