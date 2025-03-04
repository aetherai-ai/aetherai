#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Decentralized Identity (DID) Management API
"""

import json
import uuid
from flask import request, jsonify, current_app
from app.api import api_bp
from app.blockchain.did import create_did, verify_did, update_did
from app.utils.auth import token_required
from app.database.models import save_identity, get_identity, list_identities

@api_bp.route('/identity', methods=['POST'])
def create_identity():
    """Create new decentralized identity"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('name') or not data.get('public_key'):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Generate DID identifier
        did_id = f"did:example:{uuid.uuid4().hex}"
        
        # Create DID document
        did_document = {
            "id": did_id,
            "name": data.get('name'),
            "publicKey": data.get('public_key'),
            "created": data.get('created'),
            "authentication": [
                {
                    "type": "Ed25519VerificationKey2020",
                    "publicKeyMultibase": data.get('public_key')
                }
            ]
        }
        
        # Store DID document on blockchain
        tx_hash = create_did(did_id, json.dumps(did_document))
        
        # Save to database
        identity_id = save_identity({
            "did": did_id,
            "document": did_document,
            "tx_hash": tx_hash,
            "owner": data.get('owner', 'anonymous'),
            "status": "active"
        })
        
        return jsonify({
            "success": True,
            "did": did_id,
            "tx_hash": tx_hash,
            "identity_id": identity_id
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Failed to create identity: {str(e)}")
        return jsonify({"error": f"Failed to create identity: {str(e)}"}), 500

@api_bp.route('/identity/<did_id>', methods=['GET'])
def get_identity_by_did(did_id):
    """Get identity information by DID"""
    try:
        # Get identity from database
        identity = get_identity(did_id)
        
        if not identity:
            return jsonify({"error": "Identity not found"}), 404
        
        # Verify DID on blockchain
        is_valid = verify_did(did_id, json.dumps(identity.get('document')))
        
        return jsonify({
            "identity": identity,
            "verified": is_valid
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Failed to get identity: {str(e)}")
        return jsonify({"error": f"Failed to get identity: {str(e)}"}), 500

@api_bp.route('/identity', methods=['GET'])
@token_required
def list_user_identities(current_user):
    """List all identities for user"""
    try:
        # Get all identities for user
        identities = list_identities(current_user.get('id'))
        
        return jsonify({
            "identities": identities,
            "count": len(identities)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Failed to get identity list: {str(e)}")
        return jsonify({"error": f"Failed to get identity list: {str(e)}"}), 500

@api_bp.route('/identity/<did_id>', methods=['PUT'])
@token_required
def update_identity(current_user, did_id):
    """Update identity information"""
    try:
        data = request.get_json()
        
        # Get existing identity
        identity = get_identity(did_id)
        
        if not identity:
            return jsonify({"error": "Identity not found"}), 404
        
        # Verify ownership
        if identity.get('owner') != current_user.get('id'):
            return jsonify({"error": "No permission to update this identity"}), 403
        
        # Update DID document
        updated_document = identity.get('document').copy()
        if data.get('name'):
            updated_document['name'] = data.get('name')
        if data.get('public_key'):
            updated_document['publicKey'] = data.get('public_key')
            updated_document['authentication'][0]['publicKeyMultibase'] = data.get('public_key')
        
        # Update DID on blockchain
        tx_hash = update_did(did_id, json.dumps(updated_document))
        
        # Update database
        save_identity({
            "did": did_id,
            "document": updated_document,
            "tx_hash": tx_hash,
            "owner": current_user.get('id'),
            "status": "active"
        })
        
        return jsonify({
            "success": True,
            "did": did_id,
            "tx_hash": tx_hash
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Failed to update identity: {str(e)}")
        return jsonify({"error": f"Failed to update identity: {str(e)}"}), 500 