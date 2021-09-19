from os import listdir
from os.path import isfile, join
import shutil
import os
from collections import Counter


mypath = '/home/abhay/Downloads/New_Dataset/Aadhar Back/Batch_1_results/All'
# '/home/abhay/Downloads/New_Dataset/Batch_1_results/All'

onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

name_list = []

for i in onlyfiles:
    name = i.split('.')
    name_list.extend(name)

name_list_upd = list(filter(('txt').__ne__, name_list))
name_list_upd = list(filter(('jpg').__ne__, name_list_upd))

remove_able = []
CntList = Counter(name_list_upd)

cnt = 0
for i, j in CntList.items():
    if j == 1:
        new = i+'.jpg'
        remove_able.append(new)
        cnt += 1

print(cnt)

destination = '/home/abhay/Downloads/New_Dataset/Aadhar Back/TempFile'

if not os.path.exists(destination):
    os.mkdir(destination)

for file_name in remove_able:
    shutil.move(os.path.join(mypath, file_name), os.path.join(destination, file_name))
