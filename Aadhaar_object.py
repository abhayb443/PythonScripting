detected_text= ['Number', '4726 7299 0081', 'Name', 'Navneet', 'Nayal', 'Gender', 'Male']
detected_text= ['Number', '2538 0039 4560', 'Name', 'Abdul Nafi', 'DateofBirth', 'U3e 3F I Year of Birth : 199', 'Gender', 'oo I Male']
detected_text= ['Name', 'Rahul Ahirwar', 'DateofBirth', '5/02/199', '1', 'o-H DOB', 'Gender', '99 Male', 'Number', '7987 8685 6945']
detected_text= ['Name', 'Krishnamoorthy', 'Sankaranarayanan', 'DateofBirth', 'mins I DOB : 17/06/1984', '5Ii', 'Gender', '/', 'MALE', 'Number', '9507 1360 9250']
detected_text = ['Name', 'oT9T', 'DateofBirth', 'ARTA/DOB: 14/05/1995', 'Gender', 'y7q/', 'MALE', 'Number', '8755 1775 9735']
detected_text = ['Number', '6008 9344 1710', 'Name', 'Rupesh Singare', 'DateofBirth', 'P', 'DoB', '27101/2000', 'Gender', 'JPr/Male']

for i in detected_text:
    if i == 'Number':
        pos = detected_text.index(i)
        start = pos + 1
        for j in detected_text[start:]:
            if j in ['Name', 'DateofBirth', 'Gender']:
                end = detected_text.index(j)
            else:
                end = start + 1
                print(" ".join(detected_text[start: end]))
                break

    elif i == 'Name':
        pos = detected_text.index(i)
        start = pos + 1
        for j in detected_text[start:]:
            if j in ['Number', 'DateofBirth', 'Gender']:
                end = detected_text.index(j)
            else:
                end = start + 1
                print(" ".join(detected_text[start: end]))
                break

    elif i == 'Gender':
        pos = detected_text.index(i)
        start = pos + 1
        for j in detected_text[start:]:
            if j in ['Number', 'DateofBirth', 'Name']:
                end = detected_text.index(j)
            else:
                end = start + 1
                print(" ".join(detected_text[start: end]))
                break

    elif i == 'DateofBirth':
        pos = detected_text.index(i)
        start = pos + 1
        for j in detected_text[start:]:
            if j in ['Number', 'Name', 'Gender']:
                end = detected_text.index(j)
            else:
                end = start + 1
                print(" ".join(detected_text[start: end]))
                break