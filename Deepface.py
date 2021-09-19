from deepface import DeepFace
import os
import timeit


start = timeit.timeit()
File_dir = os.path.dirname(__file__)
file_path_1 = os.path.join(File_dir, 'figures/ImTab_1.jpg')
file_path_2 = os.path.join(File_dir, 'figures/AmTab.jpeg')

result = DeepFace.verify(file_path_1, file_path_2, model_name='Facenet')
print(result)
print("Is verified: ", result["verified"])
end = timeit.timeit()
print("Time Taken is - ", end - start)