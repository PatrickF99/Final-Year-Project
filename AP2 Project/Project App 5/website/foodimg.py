import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
from PIL import Image

model_url = "https://tfhub.dev/google/imagenet/mobilenet_v2_100_224/classification/5"
model = tf.keras.Sequential([hub.KerasLayer(model_url)])

def predict_food_image(image_file):
   
    image = Image.open(image_file)
    image = np.array(image.resize((224, 224)))

    
    image = image / 255.0  
    image = np.expand_dims(image, axis=0)  

    
    predictions = model.predict(image)[0]
    top_prediction_idx = np.argmax(predictions)
    top_prediction_score = predictions[top_prediction_idx]

    
    categories_url = "https://tfhub.dev/google/imagenet/imagenet_categories/3"
    categories = np.array(tf.keras.utils.get_file('ImageNetLabels.txt', categories_url))
    top_prediction_name = categories[top_prediction_idx].strip()

    
    return top_prediction_name, top_prediction_score