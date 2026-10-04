import os
import numpy as np
from PIL import Image, ImageFilter, ImageOps

try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False

def preprocess_medical_image(image_path, target_size=(224, 224)):
    """
    Applies standard medical image preprocessing pipeline:
    1. Resizing to target input shape (224x224)
    2. Grayscale & Contrast Normalization (CLAHE / Histogram Equalization)
    3. Noise Reduction (Gaussian Blur)
    4. Saves preprocessed output for visual verification
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Medical scan file not found: {image_path}")

    dir_name, file_name = os.path.split(image_path)
    preprocessed_filename = f"prep_{file_name}"
    preprocessed_path = os.path.join(dir_name, preprocessed_filename)

    if HAS_OPENCV:
        img = cv2.imread(image_path)
        if img is None:
            pil_img = Image.open(image_path).convert('RGB')
            img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        denoised = cv2.GaussianBlur(gray, (3, 3), 0)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        equalized = clahe.apply(denoised)
        resized = cv2.resize(equalized, target_size, interpolation=cv2.INTER_AREA)
        rgb_preprocessed = cv2.cvtColor(resized, cv2.COLOR_GRAY2RGB)
        cv2.imwrite(preprocessed_path, rgb_preprocessed)
        normalized_array = rgb_preprocessed.astype('float32') / 255.0
        return normalized_array, preprocessed_path
    else:
        # Robust Pure PIL / Pillow Fallback Pipeline
        pil_img = Image.open(image_path).convert('L')
        denoised = pil_img.filter(ImageFilter.GaussianBlur(radius=1))
        equalized = ImageOps.equalize(denoised)
        resized = equalized.resize(target_size, Image.Resampling.LANCZOS)
        rgb_preprocessed = resized.convert('RGB')
        rgb_preprocessed.save(preprocessed_path)
        normalized_array = np.array(rgb_preprocessed, dtype=np.float32) / 255.0
        return normalized_array, preprocessed_path
