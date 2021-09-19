from deepface import DeepFace
import os
import boto3
import timeit


def deep_face(sourceFile, targetFile):
    start = timeit.timeit()
    File_dir = os.path.dirname(__file__)
    file_path_1 = os.path.join(File_dir, 'figures/ImTab_1.jpg')
    file_path_2 = os.path.join(File_dir, 'figures/AmTab.jpeg')

    result = DeepFace.verify(file_path_1, file_path_2, model_name='Facenet')
    print(result)
    print("Is verified: ", result["verified"])
    end = timeit.timeit()
    print("Time Taken is - ", end - start)
    return result


def compare_faces(sourceFile, targetFile):
    client = boto3.client('rekognition',
                          region_name='ap-south-1',
                          aws_access_key_id='AKIA5X72HLKI6BNWMVPC',
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


if __name__ == "__main__":
    pass
