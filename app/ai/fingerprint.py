#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Fingerprint Recognition AI Module
"""

import os
import uuid
import base64
import numpy as np
import cv2
from PIL import Image
from io import BytesIO
from sklearn.metrics.pairwise import cosine_similarity

# Dictionary to store fingerprint features (should use database in production)
fingerprint_templates = {}

def register_fingerprint(fingerprint_data, user_id=None):
    """Register fingerprint features"""
    try:
        # Decode fingerprint data
        fingerprint_image = decode_fingerprint_data(fingerprint_data)
        
        if fingerprint_image is None:
            return None, None
        
        # Extract fingerprint features
        fingerprint_template = extract_fingerprint_features(fingerprint_image)
        
        if fingerprint_template is None:
            print("Failed to extract fingerprint features")
            return None, None
        
        # Generate unique ID
        fingerprint_id = str(uuid.uuid4())
        
        # Store fingerprint features
        fingerprint_templates[fingerprint_id] = {
            "template": fingerprint_template,
            "user_id": user_id
        }
        
        return fingerprint_id, fingerprint_template
        
    except Exception as e:
        print(f"Fingerprint feature registration failed: {str(e)}")
        return None, None

def verify_fingerprint(fingerprint_data, fingerprint_id=None, return_template=False):
    """Verify fingerprint features"""
    try:
        # Decode fingerprint data
        fingerprint_image = decode_fingerprint_data(fingerprint_data)
        
        if fingerprint_image is None:
            return (False, 0.0) if not return_template else None
        
        # Extract fingerprint features
        fingerprint_template = extract_fingerprint_features(fingerprint_image)
        
        if fingerprint_template is None:
            print("Failed to extract fingerprint features")
            return (False, 0.0) if not return_template else None
        
        # If only feature template is needed
        if return_template:
            return fingerprint_template
        
        # If no fingerprint_id provided, return feature template
        if fingerprint_id is None:
            return (False, 0.0)
        
        # Get stored fingerprint features
        stored_fingerprint = fingerprint_templates.get(fingerprint_id)
        
        if not stored_fingerprint:
            print(f"Fingerprint ID not found: {fingerprint_id}")
            return (False, 0.0)
        
        # Compare fingerprint features
        stored_template = stored_fingerprint["template"]
        similarity = compare_fingerprint_templates(stored_template, fingerprint_template)
        
        # Determine if match
        threshold = float(os.getenv("FINGERPRINT_MATCH_THRESHOLD", 0.7))
        is_match = similarity >= threshold
        
        return (is_match, similarity)
        
    except Exception as e:
        print(f"Fingerprint feature verification failed: {str(e)}")
        return (False, 0.0) if not return_template else None

def decode_fingerprint_data(fingerprint_data):
    """Decode fingerprint data"""
    try:
        # If Base64 string
        if isinstance(fingerprint_data, str):
            # Remove prefix if Base64 string contains it
            if ',' in fingerprint_data:
                fingerprint_data = fingerprint_data.split(',')[1]
            
            # Decode Base64
            image_data = base64.b64decode(fingerprint_data)
            
            # Convert to PIL image
            image = Image.open(BytesIO(image_data))
            
            # Convert to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            return cv_image
        
        # If binary data
        elif isinstance(fingerprint_data, bytes):
            # Convert to PIL image
            image = Image.open(BytesIO(fingerprint_data))
            
            # Convert to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            return cv_image
        
        # If NumPy array
        elif isinstance(fingerprint_data, np.ndarray):
            return fingerprint_data
        
        else:
            print(f"Unsupported fingerprint data type: {type(fingerprint_data)}")
            return None
        
    except Exception as e:
        print(f"Failed to decode fingerprint data: {str(e)}")
        return None

def extract_fingerprint_features(fingerprint_image):
    """Extract fingerprint features"""
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(fingerprint_image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive threshold
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
        
        # Find fingerprint feature points (using SIFT or ORB)
        # Note: In production, should use more professional fingerprint feature extraction algorithms
        orb = cv2.ORB_create()
        keypoints, descriptors = orb.detectAndCompute(thresh, None)
        
        # If no feature points detected
        if descriptors is None or len(descriptors) == 0:
            return None
        
        # Return feature descriptors
        return descriptors
        
    except Exception as e:
        print(f"Failed to extract fingerprint features: {str(e)}")
        return None

def compare_fingerprint_templates(template1, template2):
    """Compare fingerprint feature templates"""
    try:
        # Calculate cosine similarity between feature vectors
        similarity = cosine_similarity(template1.reshape(1, -1), template2.reshape(1, -1))[0][0]
        return similarity
        
    except Exception as e:
        print(f"Failed to compare fingerprint templates: {str(e)}")
        return 0.0 