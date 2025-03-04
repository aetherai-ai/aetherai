#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Application Initialization Module
"""

import os
from flask import Flask
from flask_cors import CORS

def create_app(test_config=None):
    """Create and configure Flask application instance"""
    
    # Create Flask application
    app = Flask(__name__, instance_relative_config=True)
    
    # Configure application
    if test_config is None:
        # Load default configuration
        app.config.from_mapping(
            SECRET_KEY=os.getenv("SECRET_KEY", "dev"),
            MONGODB_URI=os.getenv("MONGODB_URI", "mongodb://localhost:27017/did_system"),
        )
    else:
        # Load test configuration
        app.config.from_mapping(test_config)
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register index route
    @app.route('/')
    def index():
        return {
            "name": "Decentralized Identity Authentication System (DID)",
            "version": "1.0.0",
            "status": "running"
        }
    
    return app 