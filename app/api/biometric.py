#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Biometric Identity Verification API Module
"""

import os
import base64
import uuid
import numpy as np
from flask import request, jsonify, current_app
from app.api import api_bp
from app.utils.auth import token_required
from app.database.models import get_user_biometrics, save_user_biometrics
from app.ai.face_recognition import verify_face, register_face
from app.ai.fingerprint import verify_fingerprint, register_fingerprint
from app.blockchain.biometric import store_biometric_hash, verify_biometric_hash

@api_bp.route('/biometric/register/face', methods=['POST'])
@token_required
def register_face_biometric(current_user):
    """Register facial biometric features"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('face_image'):
            return jsonify({"error": "Missing face image data"}), 400
        
        # Decode Base64 image
        face_image_base64 = data.get('face_image')
        
        # Register facial features
        face_id, face_embedding = register_face(
            face_image_base64, 
            user_id=current_user.get('id')
        )
        
        if not face_id:
            return jsonify({"error": "Face registration failed, no valid face detected"}), 400
        
        # Calculate face feature hash (for blockchain storage)
        face_hash = hash(str(face_embedding))
        
        # Store hash in blockchain
        tx_hash = store_biometric_hash(
            current_user.get('did'),
            "face",
            face_hash
        )
        
        # Save to database
        biometric_id = save_user_biometrics({
            "user_id": current_user.get('id'),
            "type": "face",
            "biometric_id": face_id,
            "tx_hash": tx_hash,
            "status": "active"
        })
        
        return jsonify({
            "success": True,
            "message": "Facial biometric registration successful",
            "biometric_id": biometric_id,
            "tx_hash": tx_hash
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Facial biometric registration failed: {str(e)}")
        return jsonify({"error": f"Facial biometric registration failed: {str(e)}"}), 500

@api_bp.route('/biometric/verify/face', methods=['POST'])
def verify_face_biometric():
    """Verify facial biometric features"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('face_image') or not data.get('did'):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Decode Base64 image
        face_image_base64 = data.get('face_image')
        did = data.get('did')
        
        # Get user biometric information
        user_biometrics = get_user_biometrics(did, "face")
        
        if not user_biometrics:
            return jsonify({"error": "No facial biometric record found for user"}), 404
        
        # Verify facial features
        is_match, confidence = verify_face(
            face_image_base64,
            user_biometrics.get('biometric_id')
        )
        
        # Get threshold configuration
        threshold = float(os.getenv("FACE_RECOGNITION_THRESHOLD", 0.6))
        
        # Verify biometric hash on blockchain
        blockchain_verified = False
        if is_match and confidence >= threshold:
            # Calculate current face feature hash
            face_embedding = verify_face(face_image_base64, None, return_embedding=True)
            face_hash = hash(str(face_embedding))
            
            # Verify hash on blockchain
            blockchain_verified = verify_biometric_hash(
                did,
                "face",
                face_hash
            )
        
        return jsonify({
            "verified": is_match and confidence >= threshold,
            "confidence": float(confidence),
            "threshold": threshold,
            "blockchain_verified": blockchain_verified
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Facial biometric verification failed: {str(e)}")
        return jsonify({"error": f"Facial biometric verification failed: {str(e)}"}), 500

@api_bp.route('/biometric/register/fingerprint', methods=['POST'])
@token_required
def register_fingerprint_biometric(current_user):
    """Register fingerprint biometric features"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('fingerprint_data'):
            return jsonify({"error": "Missing fingerprint data"}), 400
        
        # Decode fingerprint data
        fingerprint_data = data.get('fingerprint_data')
        
        # Register fingerprint features
        fingerprint_id, fingerprint_template = register_fingerprint(
            fingerprint_data,
            user_id=current_user.get('id')
        )
        
        if not fingerprint_id:
            return jsonify({"error": "Fingerprint registration failed, no valid fingerprint detected"}), 400
        
        # Calculate fingerprint feature hash (for blockchain storage)
        fingerprint_hash = hash(str(fingerprint_template))
        
        # Store hash in blockchain
        tx_hash = store_biometric_hash(
            current_user.get('did'),
            "fingerprint",
            fingerprint_hash
        )
        
        # Save to database
        biometric_id = save_user_biometrics({
            "user_id": current_user.get('id'),
            "type": "fingerprint",
            "biometric_id": fingerprint_id,
            "tx_hash": tx_hash,
            "status": "active"
        })
        
        return jsonify({
            "success": True,
            "message": "Fingerprint biometric registration successful",
            "biometric_id": biometric_id,
            "tx_hash": tx_hash
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Fingerprint biometric registration failed: {str(e)}")
        return jsonify({"error": f"Fingerprint biometric registration failed: {str(e)}"}), 500

@api_bp.route('/biometric/verify/fingerprint', methods=['POST'])
def verify_fingerprint_biometric():
    """Verify fingerprint biometric features"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('fingerprint_data') or not data.get('did'):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Decode fingerprint data
        fingerprint_data = data.get('fingerprint_data')
        did = data.get('did')
        
        # Get user biometric information
        user_biometrics = get_user_biometrics(did, "fingerprint")
        
        if not user_biometrics:
            return jsonify({"error": "No fingerprint biometric record found for user"}), 404
        
        # Verify fingerprint features
        is_match, confidence = verify_fingerprint(
            fingerprint_data,
            user_biometrics.get('biometric_id')
        )
        
        # Get threshold configuration
        threshold = float(os.getenv("FINGERPRINT_MATCH_THRESHOLD", 0.7))
        
        # Verify biometric hash on blockchain
        blockchain_verified = False
        if is_match and confidence >= threshold:
            # Calculate current fingerprint feature hash
            fingerprint_template = verify_fingerprint(fingerprint_data, None, return_template=True)
            fingerprint_hash = hash(str(fingerprint_template))
            
            # Verify hash on blockchain
            blockchain_verified = verify_biometric_hash(
                did,
                "fingerprint",
                fingerprint_hash
            )
        
        return jsonify({
            "verified": is_match and confidence >= threshold,
            "confidence": float(confidence),
            "threshold": threshold,
            "blockchain_verified": blockchain_verified
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Fingerprint biometric verification failed: {str(e)}")
        return jsonify({"error": f"Fingerprint biometric verification failed: {str(e)}"}), 500 