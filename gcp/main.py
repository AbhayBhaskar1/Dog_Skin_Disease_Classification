from google.cloud import storage
import tensorflow as tf
from PIL import Image
import numpy as np

model = None
class_names = ["Bacterial_dermatosis", "Fungal_infections", "Healthy", "Hypersensitivity_allergic_dermatosis"]
BUCKET_NAME = "dog_disease_classification"  # Replace with your bucket name

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)

    print(f"Blob {source_blob_name} downloaded to {destination_file_name}.")

def load_model():
    global model
    if model is None:
        download_blob(BUCKET_NAME, "models/dog.h5", "/tmp/dog.h5")
        model = tf.keras.models.load_model("/tmp/dog.h5")

def predict(request):
    global model
    load_model()

    try:
        image = request.files["file"]
        img = Image.open(image).convert("RGB").resize((256, 256))
        img = np.array(img) / 255.0  # Normalize the image
        img_array = tf.expand_dims(img, 0)
        
        predictions = model.predict(img_array)
        predicted_class = class_names[np.argmax(predictions[0])]
        confidence = round(100 * np.max(predictions[0]), 2)

        return {"class": predicted_class, "confidence": confidence}
    except Exception as e:
        return {"error": str(e)}
