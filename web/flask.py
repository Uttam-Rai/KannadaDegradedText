from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import json
from tensorflow.keras.models import load_model
import numpy as np
from PIL import Image

# Flask app setup
app = Flask(__name__)

# Path to the final_model folder
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'final_model')

# Flask configuration
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

# Ensure the uploads folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Load model and config
def load_model_from_file():
    try:
        model = load_model(os.path.join(MODEL_PATH, 'model.weights.h5'))
        with open(os.path.join(MODEL_PATH, 'config.json'), 'r') as f:
            config = json.load(f)
        return model, config
    except Exception as e:
        print(f"Error loading model: {e}")
        return None, None

# Load model globally
model, config = load_model_from_file()

# Kannada letter mapping from class ID (0-46)
letter_mapping = [
    'ಅ', 'ಆ', 'ಇ', 'ಈ', 'ಉ', 'ಊ', 'ಋ', 'ೠ', 'ಌ', 'ೡ',
    'ಎ', 'ಏ', 'ಐ', 'ಒ', 'ಓ', 'ಊ', 'ಋ', 'ೠ', 'ಕ', 'ಖ',
    'ಗ', 'ಘ', 'ಙ', 'ಚ', 'ಛ', 'ಜ', 'ಝ', 'ಞ', 'ಟ', 'ಠ',
    'ಡ', 'ಢ', 'ಣ', 'ತ', 'ಥ', 'ದ', 'ಧ', 'ನ', 'ಪ', 'ಫ',
    'ಬ', 'ಭ', 'ಮ', 'ಯ', 'ರ', 'ಲ', 'ವ', 'ಶ', 'ಷ', 'ಸ',
    'ಹ', 'ಳ', 'ಕ್ಷ', 'ಞ', 'ಃ'
]

# Serve index.html
@app.route('/')
def index():
    return send_from_directory('web', 'index.html')

# Route to handle image upload and prediction
@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Preprocess and predict the class
        predicted_class = predict_class_from_image(file_path)
        
        if predicted_class == -1:  # Error in prediction
            return jsonify({"error": "Prediction failed"}), 500
        
        # Get Kannada letter
        predicted_letter = letter_mapping[predicted_class]
        return jsonify({"predicted_letter": predicted_letter}), 200
    
    return jsonify({"error": "Invalid file type"}), 400

# Preprocessing and prediction function
def preprocess_image(image_path):
    try:
        # Open the image and preprocess it (resize, normalize, etc.)
        image = Image.open(image_path).convert('RGB')
        image = image.resize((224, 224))  # Resize to model input size
        image = np.array(image) / 255.0  # Normalize to [0, 1]
        image = np.expand_dims(image, axis=0)  # Add batch dimension
        return image
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        return None

def predict_class_from_image(image_path):
    image = preprocess_image(image_path)
    if image is None:
        return -1
    
    try:
        prediction = model.predict(image)  # Get prediction from model
        predicted_class = np.argmax(prediction, axis=-1)[0]  # Get the predicted class index
        return predicted_class
    except Exception as e:
        print(f"Prediction error: {e}")
        return -1  # Return a default invalid class in case of error

# Error handler for 404 errors
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    app.run(debug=False)
