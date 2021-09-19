import matplotlib.pyplot as plt
import numpy as np
import os
import PIL
import tensorflow as tf
import pickle
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential

test_data_dir = "/home/abhay/Desktop/Dataset/selfies_passport/real"
# test_data_dir = "/home/abhay/Downloads/passportpic1.jpeg"

# test_data_list = []
#
# for path, subdirs, files in os.walk(test_data_dir):
#     for name in files:
#         test_data_list.append(os.path.join(path, name))

# print(test_data_list)

img_height = 180
img_width = 180

model = tf.keras.models.load_model('/home/abhay/Downloads/liveness_model_V2.h5')
label = pickle.loads(open('/home/abhay/Downloads/Liveness_classification_labels_v2.pickle', "rb").read())

# image = test_data_list[0]
image = "/home/abhay/Downloads/passportpic1.jpeg"
print(type(image))
image = bytes(image, 'utf-8')
# image = image.decode("utf-8")
print(type(image))

load_img = keras.preprocessing.image.load_img(image, target_size=(img_height, img_width))
img_processing = keras.preprocessing.image.img_to_array(load_img)
img_processed = tf.expand_dims(img_processing, 0)  # Create a batch

predictions = model.predict(img_processed)
score = tf.nn.softmax(predictions[0])

print("This image most likely belongs to {} with a {:.2f} percent confidence.".format(label[np.argmax(score)], 100 * np.max(score)))
