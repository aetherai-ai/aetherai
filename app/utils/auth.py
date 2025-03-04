#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Authentication Utility Module
"""

import os
import jwt
from functools import wraps
from flask import request, jsonify, current_app
from app.database.models import get_user_by_did

def token_required(f):
    """JWT token verification decorator"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from request header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({"error": "Missing authentication token"}), 401
        
        try:
            # Decode token
            payload = jwt.decode(
                token,
                os.getenv("JWT_SECRET", "dev-secret"),
                algorithms=["HS256"]
            )
            
            # Get user information
            current_user = get_user_by_did(payload['did'])
            
            if not current_user:
                return jsonify({"error": "Invalid user"}), 401
            
            # Convert ObjectId to string
            if "_id" in current_user:
                current_user["id"] = str(current_user["_id"])
            
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        # Pass current user to decorated function
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Administrator permission verification decorator"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        # Check if user has administrator permissions
        if not current_user.get('is_admin', False):
            return jsonify({"error": "Administrator permissions required"}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated 