# ml/vehicle_predictor.py

import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
from PIL import Image
import os

# Load model only once (global)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "complete_model_model.h5")

print("🚀 Loading vehicle classification model...")
model = tf.keras.models.load_model(MODEL_PATH)
print("✅ Model loaded successfully!")

# Must match your training class order
CLASS_NAMES = [
    'Ambulance', 'Bicycle', 'Boat', 'Bus', 'Car', 'Helicopter', 'Limousine',
    'Motorcycle', 'PickUp', 'Segway', 'Snowmobile', 'Tank', 'Taxi', 'Truck', 'Van'
]

IMG_SIZE = (224, 224)  # Same as training size

def predict_vehicle_type(image_field):
    """
    Takes an InMemoryUploadedFile (Django uploaded image),
    saves temporarily, runs prediction, and returns predicted class.
    """
    try:
        # Load and preprocess image
        img = Image.open(image_field).convert("RGB")
        img = img.resize(IMG_SIZE)
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0  # normalize if trained on normalized images

        # Predict
        predictions = model.predict(img_array)
        predicted_index = np.argmax(predictions[0])
        predicted_label = CLASS_NAMES[predicted_index]
        confidence = float(predictions[0][predicted_index])

        return predicted_label, confidence
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return None, None
