import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_datasets as tfds

# Load the pre-trained Inception-v3 model
module_url = "https://tfhub.dev/google/imagenet/inception_v3/feature_vector/5"
module = hub.KerasLayer(module_url, input_shape=(299, 299, 3), trainable=False)

# Load the Food-101 dataset
data, info = tfds.load("food101", split="train", with_info=True)

# Split the dataset into training and validation sets
train_data = data.take(10000).map(lambda x: (x['image'], x['label']))
train_data = train_data.map(lambda x, y: (tf.image.resize(x, (299, 299)), y)).batch(32)
val_data = data.skip(10000).map(lambda x: (x['image'], x['label']))
val_data = val_data.map(lambda x, y: (tf.image.resize(x, (299, 299)), y)).batch(32)

# Create a new output layer for 101 classes and train the model
model = tf.keras.Sequential([
  module,
  tf.keras.layers.Dense(101, activation="softmax")
])

model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
model.fit(train_data, epochs=5, validation_data=val_data)

# Save the trained model to your local directory
model.save("my_model")
