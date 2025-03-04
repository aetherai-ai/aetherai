#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API Blueprint Module
"""

from flask import Blueprint

# Create API blueprint
api_bp = Blueprint('api', __name__)

# Import routes
from app.api import identity, auth, biometric, fraud_detection

# Register route handler
@api_bp.route('/')
def index():
    """API root path handler"""
    return {
        "message": "Welcome to DID System API",
        "version": "1.0.0",
        "endpoints": [
            "/api/identity",
            "/api/auth",
            "/api/biometric",
            "/api/fraud"
        ]
    } 