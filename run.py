#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Decentralized Identity Authentication System (DID) Main Runner
"""

import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables
load_dotenv()

# Create application instance
app = create_app()

if __name__ == "__main__":
    # Get configurations
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    # Run application
    print(f"Starting DID System, access at: http://{host}:{port}")
    app.run(host=host, port=port, debug=debug) 