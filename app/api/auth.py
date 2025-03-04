#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Authentication API Module
"""

import os
import jwt
import datetime
from flask import request, jsonify, current_app
from app.api import api_bp
from app.database.models import get_user_by_did, create_user, verify_user_credentials
from app.utils.crypto import verify_signature
from app.blockchain.did import verify_did

@api_bp.route('/auth/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('did') or not data.get('username') or not data.get('password'):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Check if DID is valid
        did_id = data.get('did')
        is_valid_did = verify_did(did_id, None)  # Only verify DID existence
        
        if not is_valid_did:
            return jsonify({"error": "Invalid DID"}), 400
        
        # Check if username already exists
        existing_user = get_user_by_did(did_id)
        if existing_user:
            return jsonify({"error": "User already exists"}), 409
        
        # Create new user
        user_id = create_user({
            "did": did_id,
            "username": data.get('username'),
            "password": data.get('password'),  # Password will be hashed in create_user function
            "email": data.get('email', ''),
            "created_at": datetime.datetime.utcnow()
        })
        
        return jsonify({
            "success": True,
            "message": "User registration successful",
            "user_id": user_id
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"User registration failed: {str(e)}")
        return jsonify({"error": f"User registration failed: {str(e)}"}), 500

@api_bp.route('/auth/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or (not data.get('did') and not data.get('username')) or not data.get('password'):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Verify user credentials
        user = verify_user_credentials(
            did=data.get('did'),
            username=data.get('username'),
            password=data.get('password')
        )
        
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Generate JWT token
        token_payload = {
            "sub": user.get('_id'),
            "did": user.get('did'),
            "username": user.get('username'),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=int(os.getenv("TOKEN_EXPIRY", 86400)))
        }
        
        token = jwt.encode(
            token_payload,
            os.getenv("JWT_SECRET", "dev-secret"),
            algorithm="HS256"
        )
        
        return jsonify({
            "success": True,
            "token": token,
            "user": {
                "id": user.get('_id'),
                "did": user.get('did'),
                "username": user.get('username')
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"User login failed: {str(e)}")
        return jsonify({"error": f"User login failed: {str(e)}"}), 500

@api_bp.route('/auth/verify-signature', methods=['POST'])
def verify_did_signature():
    """Verify DID signature"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('did') or not data.get('message') or not data.get('signature'):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Get DID document
        did_id = data.get('did')
        did_doc = verify_did(did_id, None, return_doc=True)
        
        if not did_doc:
            return jsonify({"error": "Invalid DID"}), 400
        
        # Verify signature
        public_key = did_doc.get('publicKey')
        message = data.get('message')
        signature = data.get('signature')
        
        is_valid = verify_signature(public_key, message, signature)
        
        return jsonify({
            "valid": is_valid,
            "did": did_id
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Signature verification failed: {str(e)}")
        return jsonify({"error": f"Signature verification failed: {str(e)}"}), 500 