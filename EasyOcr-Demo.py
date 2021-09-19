# Easy OCR
# https://github.com/bhattbhavesh91/easyocr-demo/blob/master/easy-ocr-demo-notebook.ipynb

import matplotlib.pyplot as plt
import cv2
import easyocr
import os
import timeit
from pylab import rcParams

from IPython.display import Image
rcParams['figure.figsize'] = 8, 16

reader = easyocr.Reader(['en'])

starttime = timeit.timeit()
dir = os.path.dirname(__file__)

img_array = ['1599247681146752.jpg',
'1599247681146752-lbl.jpg',
'1599248184789463.jpg',
'1599248184789463-lbl.jpg',
'1599249988896975.jpg',
'1599252179118761.jpg',
'1599252558764156.jpg',
'1599256393515379.jpg',
'1599257934229847.jpg',
'1599259224611258.jpg',
'1599259897471375.jpg',
'1599261528371975.jpg']

starttime = timeit.timeit()

res = []

for i in img_array:
    filename = os.path.join(dir, 'figures/{}'.format(i))
    output = reader.readtext(filename, detail=0)
    address = [x for x in output]
    address = str(address).replace("'", "").replace('[', '').replace(']', '')
    res.append(address)

Endtime = timeit.timeit()

print(Endtime - starttime)
print(res)
# Then we would be running address regex to verify the accuracy of the address



"""
Image - 1599247681146752.jpg 
[([[288, 16], [450, 16], [450, 48], [288, 48]], '14{2}&"419 4|#', 3.9804243101571046e-07), 
([[458, 20], [556, 20], [556, 46], [458, 46]], 'Hifelel"T', 0.00626685144379735), 
([[204, 22], [278, 22], [278, 48], [204, 48]], 'zTeclq', 0.07211340218782425), 
([[248, 48], [580, 48], [580, 72], [248, 72]], 'leglfiCAllOrg AuitfIP3TV OFTIIDIA', 5.3708010261388495e-12), 
([[60, 90], [146, 90], [146, 114], [60, 114]], 'Address', 0.929323136806488), 
([[60, 109], [402, 109], [402, 136], [60, 136]], 'SIO Vijay Kumar A/164 housing board', 0.08202754706144333), 
([[57, 134], [282, 134], [282, 160], [57, 160]], 'colony Hanumangarh jn.', 0.45199137926101685), 
([[300, 154], [374, 154], [374, 180], [300, 180]], '335512', 0.7693307399749756), 
([[59, 155], [290, 155], [290, 184], [59, 184]], 'Hanumangarh Rajasthan', 0.5642659664154053), 
([[198, 261], [413, 261], [413, 299], [198, 299]], '3709 7318 9582', 0.6096310615539551), 
([[369, 305], [411, 305], [411, 321], [369, 321]], 'ar', 0.00028102591750212014), 
([[534, 314], [576, 314], [576, 344], [534, 344]], '8946;', 0.004435085691511631), 
([[487, 319], [535, 319], [535, 331], [487, 331]], '', 0.8822205662727356), 
([[205, 325], [323, 325], [323, 345], [205, 345]], 'holpelulralgov.in', 0.03712742030620575), 
([[119, 327], [149, 327], [149, 341], [119, 341]], '1947', 0.3483865261077881), 
([[337, 327], [447, 327], [447, 341], [337, 341]], 'wwuuldaigovin', 0.060765355825424194), 
([[89, 341], [181, 341], [181, 357], [89, 357]], '1000 30" 1947', 0.03088810108602047)]
"""

"""
[([[296, 81], [558, 81], [558, 108], [296, 108]], 'Unique Identiication Auharty or1ml3', 1.8824882772605633e-06), 
([[395, 111], [443, 111], [443, 125], [395, 125]], 'Adlss3', 0.007125039119273424), 
([[201, 119], [225, 119], [225, 131], [201, 131]], 'Hsil:', 0.34403249621391296), 
([[449, 125], [567, 125], [567, 141], [449, 141]], 'Pam13$113114: 914!4,', 8.626926017996084e-08), 
([[395, 127], [445, 127], [445, 141], [395, 141]], 'SluLea', 0.009049377404153347), 
([[247, 131], [351, 131], [351, 149], [247, 149]], '61& !7!|?1#7_9]+74!,', 3.0569367481803056e-08), 
([[201, 133], [243, 133], [243, 145], [201, 145]], '31]c#131:', 0.0013503438094630837), 
([[395, 139], [571, 139], [571, 159], [395, 159]], 'gran nist#avaiya D&kare4p&+,', 3.244627011511625e-09), 
([[201, 145], [347, 145], [347, 161], [201, 161]], 'JH-fHHal7T-T 9l.JlT-=T9', 4.654781449175971e-09), 
([[397, 157], [549, 157], [549, 173], [397, 173]], 'Knaril, Burar. Varnassur.', 4.0884224290493876e-05), 
([[291, 159], [371, 159], [371, 179], [291, 179]], '7#179{, f4#r7.', 2.8259157261345536e-05), 
([[251, 163], [285, 163], [285, 177], [251, 177]], '4#H!,', 0.0931340679526329), 
([[201, 165], [247, 165], [247, 179], [201, 179]], 'hdll!gT', 0.004781629890203476), 
([[397, 173], [473, 173], [473, 187], [397, 187]], 'Birer,8L21{,2', 0.0014349785633385181), 
([[200, 176], [247, 176], [247, 195], [200, 195]], '802102', 0.9687758684158325), 
([[310, 260], [474, 260], [474, 286], [310, 286]], '5426_8403_6275', 0.22440198063850403), 
([[345, 309], [419, 309], [419, 323], [345, 323]], '"=2#8_064=', 1.879426614337376e-09)]
"""

"""
[([[93, 31], [183, 31], [183, 51], [93, 51]], '400333', 0.0027856125961989164), 
([[169, 55], [241, 55], [241, 71], [169, 71]], 'arr', 7.273960363818333e-05), 
([[9, 57], [41, 57], [41, 73], [9, 73]], 'su', 0.252732515335083), 
([[47, 57], [93, 57], [93, 73], [47, 73]], '3', 0.2745001018047333), 
([[99, 57], [161, 57], [161, 71], [99, 71]], '', 0.011767392046749592), 
([[43, 75], [251, 75], [251, 93], [43, 93]], '=<=5`42175315', 2.3839969998107335e-09), 
([[11, 79], [37, 79], [37, 91], [11, 91]], '', 0.22052814066410065), 
([[219, 95], [257, 95], [257, 111], [219, 111]], 'a', 0.09751474112272263), 
([[11, 97], [51, 97], [51, 113], [11, 113]], 'a', 0.015444599092006683), 
([[143, 97], [213, 97], [213, 111], [143, 111]], '', 0.22897914052009583), 
([[57, 99], [93, 99], [93, 113], [57, 113]], 'a', 0.03663453832268715), 
([[111.10557280900008, 112.21114561800017], [160.9596081175608, 118.600079976008], [157.89442719099992, 135.78885438199984], [108.04039188243918, 129.399920023992]], 'T2', 0.05632949247956276), 
([[11, 119], [55, 119], [55, 133], [11, 133]], '', 0.0014565010787919164), 
([[65, 119], [101, 119], [101, 133], [65, 133]], '=', 0.0011171692749485373), 
([[113, 135], [165, 135], [165, 151], [113, 151]], 'zee', 0.0002563097223173827),
([[11, 139], [101, 139], [101, 153], [11, 153]], '', 0.30438292026519775)]

"""

"""
[([[12, 6], [86, 6], [86, 30], [12, 30]], 'Address', 0.9899516105651855), 
([[12, 30], [174, 30], [174, 54], [12, 54]], 'SIO: Sampath, 151', 0.2963483929634094), 
([[12, 54], [266, 54], [266, 78], [12, 78]], 'MARIYAMMANKOIL STREET', 0.28565311431884766), 
([[12, 78], [260, 78], [260, 102], [12, 102]], 'THIRUMALAIKUPPAM, Falur', 0.28612929582595825), 
([[12, 102], [248, 102], [248, 127], [12, 127]], 'Palur, Vellore, Ambur Tamil', 0.07470954209566116), 
([[12, 126], [134, 126], [134, 150], [12, 150]], 'Nadu, 635804', 0.6257185339927673)]
"""
