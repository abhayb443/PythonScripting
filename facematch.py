# import cv2
# import face_recognition
# import os
# import sys
#
#
# File_dir = os.path.dirname(__file__)
# file_path_1 = os.path.join(File_dir, 'TestData/aadhar_prf.jpg')
# file_path_2 = os.path.join(File_dir, 'TestData/aadhar_img.jpg')
#
# image_1 = face_recognition.load_image_file(file_path_1)
# image_2 = face_recognition.load_image_file(file_path_2)
#
# try:
#     Face_1_encoding = face_recognition.face_encodings(image_1)[0]
#     unknown_encoding = face_recognition.face_encodings(image_2)[0]
# except IndexError as e:
#     print(e)
#     sys.exit(1)
#
# results = face_recognition.compare_faces([Face_1_encoding], unknown_encoding)
# print(results)

import os
import boto3


File_dir = os.path.dirname(__file__)
file_path_1 = os.path.join(File_dir, 'TestData/aadharFrontJP.jpg')
file_path_2 = os.path.join(File_dir, 'TestData/ab_selfie.jpeg')


def compare_faces(sourceFile, targetFile):
    client = boto3.client('rekognition',
                            region_name='us-west-2',
                            aws_access_key_id='AKIAIMPLMZRICBK5I6SQ',
                            aws_secret_access_key='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')

    imageSource = open(sourceFile, 'rb')
    imageTarget = open(targetFile, 'rb')

    response = client.compare_faces(SimilarityThreshold=80,
                                    SourceImage={'Bytes': imageSource.read()},
                                    TargetImage={'Bytes': imageTarget.read()})

    for faceMatch in response['FaceMatches']:
        position = faceMatch['Face']['BoundingBox']
        similarity = str(faceMatch['Similarity'])
        print('The face at position one ' +
              str(position['Left']) + ' and position two ' +
              str(position['Top']) +
              ' matches with ' + similarity + '% confidence')

    imageSource.close()
    imageTarget.close()
    return len(response['FaceMatches'])


def main():
    source_file = file_path_1
    target_file = file_path_2
    face_matches = compare_faces(source_file, target_file)
    print("Face matches: " + str(face_matches))


if __name__ == "__main__":
    main()