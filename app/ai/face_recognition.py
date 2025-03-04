#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Face Recognition AI Module
"""

import os
import uuid
import base64
import numpy as np
import cv2
import face_recognition
from deepface import DeepFace
from PIL import Image
from io import BytesIO

face_embeddings = {}

def register_face(face_image_base64, user_id=None):
    """Register face features"""
    try:
        # Decode Base64 image
        face_image = decode_base64_image(face_image_base64)
        
        if face_image is None:
            return None, None
        
        # Detect face
        face_locations = face_recognition.face_locations(face_image)
        
        if not face_locations:
            print("No face detected")
            return None, None
        
        # Extract face features
        face_encoding = face_recognition.face_encodings(face_image, face_locations)[0]
        
        # Generate unique ID
        face_id = str(uuid.uuid4())
        
        # Store face features
        face_embeddings[face_id] = {
            "embedding": face_encoding,
            "user_id": user_id
        }
        
        return face_id, face_encoding
        
    except Exception as e:
        print(f"Face feature registration failed: {str(e)}")
        return None, None

def verify_face(face_image_base64, face_id=None, return_embedding=False):
    """Verify face features"""
    try:
        # Decode Base64 image
        face_image = decode_base64_image(face_image_base64)
        
        if face_image is None:
            return (False, 0.0) if not return_embedding else None
        
        # Detect face
        face_locations = face_recognition.face_locations(face_image)
        
        if not face_locations:
            print("No face detected")
            return (False, 0.0) if not return_embedding else None
        
        # Extract face features
        face_encoding = face_recognition.face_encodings(face_image, face_locations)[0]
        
        # If only feature vector is needed
        if return_embedding:
            return face_encoding
        
        # If no face_id provided, return feature vector
        if face_id is None:
            return (False, 0.0)
        
        # Get stored face features
        stored_face = face_embeddings.get(face_id)
        
        if not stored_face:
            print(f"Face ID not found: {face_id}")
            return (False, 0.0)
        
        # Compare face features
        stored_encoding = stored_face["embedding"]
        distance = face_recognition.face_distance([stored_encoding], face_encoding)[0]
        
        # Convert distance to similarity score (0-1, higher is more similar)
        similarity = 1.0 - distance
        
        # Determine if match
        is_match = similarity >= float(os.getenv("FACE_RECOGNITION_THRESHOLD", 0.6))
        
        return (is_match, similarity)
        
    except Exception as e:
        print(f"Face feature verification failed: {str(e)}")
        return (False, 0.0) if not return_embedding else None

def detect_liveness(face_image_base64):
    """Detect liveness (prevent photo attacks)"""
    try:
        # Decode Base64 image
        face_image = decode_base64_image(face_image_base64)
        
        if face_image is None:
            return False, 0.0
        
        # Use DeepFace for liveness detection
        # Note: This is a simplified implementation, real applications should use more sophisticated liveness detection
        analysis = DeepFace.analyze(face_image, actions=['emotion', 'age', 'gender', 'race'])
        
        # Check if face detected
        if not analysis:
            return False, 0.0
        
        # Simple liveness detection logic (should be more complex in real applications)
        # Here we assume if emotions can be detected, it might be a real face
        emotion_score = max(analysis[0]['emotion'].values())
        
        # Determine if live
        is_live = emotion_score > 0.5
        
        return is_live, emotion_score
        
    except Exception as e:
        print(f"Liveness detection failed: {str(e)}")
        return False, 0.0

def decode_base64_image(base64_string):
    """Decode Base64 image"""
    try:
        # Remove prefix if Base64 string contains it
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode Base64
        image_data = base64.b64decode(base64_string)
        
        # Convert to PIL image
        image = Image.open(BytesIO(image_data))
        
        # Convert to OpenCV format
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        return cv_image
        
    except Exception as e:
        print(f"Image decoding failed: {str(e)}")
        return None 