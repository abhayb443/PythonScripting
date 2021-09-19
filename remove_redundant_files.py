from os import listdir
from os.path import isfile, join
import shutil
import os
from collections import Counter


def list_duplicates(seq):
    seen = set()
    seen_add = seen.add
    # adds all elements it doesn't know yet to seen and all other to seen_twice
    seen_twice = set(x for x in seq if x in seen or seen_add(x))
    # turn the set into a list (as requested)
    return list(seen_twice)

mypath = '/home/abhay/Downloads/Model-Object-Detection/Dataset'
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

name_list = []

for i in onlyfiles:
    name = i.split('.')
    name_list.extend(name)

name_list_upd = list(filter(('txt').__ne__, name_list))
name_list_upd = list(filter(('xml').__ne__, name_list_upd))
name_list_upd = list(filter(('jpg').__ne__, name_list_upd))
name_list_upd = list(filter(('json').__ne__, name_list_upd))
dupList = list_duplicates(name_list_upd)

# print(dupList)

remove_able = []
avoid_list = ['test', 'train', 'labelled_data', 'json', 'Aadhar_front', 'data', 'names', 'predefined_classes']

# for j in name_list_upd:
#     if j not in dupList:
#         if j not in avoid_list:
#             new = j+'.jpg'
#             remove_able.append(new)

CntList = Counter(name_list)

for i, j in CntList.items():
    if i not in avoid_list:
        if j == 1:
            print(i)
            new = i+'.jpg'
            # new_1 = i+'.xml'
            # new_2 = i+'.json'
            remove_able.append(new)
            # remove_able.append(new_1)
            # remove_able.append(new_2)
        elif j == 2:
            print(i)
            new = i+'.jpg'
            # new_1 = i+'.xml'
            # new_2 = i+'.json'
            remove_able.append(new)
            # remove_able.append(new_1)
            # remove_able.append(new_2)

# print(remove_able)
print(len(remove_able))

source = '/home/abhay/Downloads/Model-Object-Detection/Dataset/'
destination = '/home/abhay/Downloads/Temp/'

if not os.path.exists(destination):
    os.mkdir(destination)

for file_name in remove_able:
    if os.path.isfile(os.path.join(destination, file_name)):
        path = os.path.join(source, file_name)
        os.remove(path)
    else:
        shutil.move(os.path.join(source, file_name), os.path.join(destination, file_name))
