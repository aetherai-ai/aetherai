#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Fraud Detection API Module
"""

import os
import json
import datetime
from flask import request, jsonify, current_app
from app.api import api_bp
from app.utils.auth import token_required
from app.ai.fraud_detection import detect_identity_fraud, detect_deepfake
from app.database.models import save_fraud_report, get_fraud_reports
from app.blockchain.fraud import report_fraud_to_blockchain

@api_bp.route('/fraud/detect/identity', methods=['POST'])
def detect_identity_fraud_api():
    """Detect identity fraud"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('identity_data'):
            return jsonify({"error": "Missing identity data"}), 400
        
        # Get identity data
        identity_data = data.get('identity_data')
        
        # Perform fraud detection
        is_fraud, fraud_score, fraud_details = detect_identity_fraud(identity_data)
        
        # If fraud detected, record to database
        report_id = None
        tx_hash = None
        if is_fraud and fraud_score > float(os.getenv("FRAUD_THRESHOLD", 0.7)):
            # Save fraud report to database
            report_id = save_fraud_report({
                "type": "identity",
                "data": identity_data,
                "score": fraud_score,
                "details": fraud_details,
                "timestamp": datetime.datetime.utcnow(),
                "status": "detected"
            })
            
            # If DID provided, record fraud report to blockchain
            if data.get('did'):
                tx_hash = report_fraud_to_blockchain(
                    data.get('did'),
                    "identity",
                    fraud_score,
                    json.dumps(fraud_details)
                )
        
        return jsonify({
            "fraud_detected": is_fraud,
            "fraud_score": float(fraud_score),
            "fraud_details": fraud_details,
            "report_id": report_id,
            "tx_hash": tx_hash
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Identity fraud detection failed: {str(e)}")
        return jsonify({"error": f"Identity fraud detection failed: {str(e)}"}), 500

@api_bp.route('/fraud/detect/deepfake', methods=['POST'])
def detect_deepfake_api():
    """Detect deepfake"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('image_data'):
            return jsonify({"error": "Missing image data"}), 400
        
        # Get image data
        image_data = data.get('image_data')
        
        # Perform deepfake detection
        is_deepfake, deepfake_score, deepfake_details = detect_deepfake(image_data)
        
        # If deepfake detected, record to database
        report_id = None
        tx_hash = None
        if is_deepfake and deepfake_score > float(os.getenv("DEEPFAKE_THRESHOLD", 0.7)):
            # Save fraud report to database
            report_id = save_fraud_report({
                "type": "deepfake",
                "data": {"image_hash": hash(image_data)},  # Store image hash instead of original image
                "score": deepfake_score,
                "details": deepfake_details,
                "timestamp": datetime.datetime.utcnow(),
                "status": "detected"
            })
            
            # If DID provided, record fraud report to blockchain
            if data.get('did'):
                tx_hash = report_fraud_to_blockchain(
                    data.get('did'),
                    "deepfake",
                    deepfake_score,
                    json.dumps(deepfake_details)
                )
        
        return jsonify({
            "deepfake_detected": is_deepfake,
            "deepfake_score": float(deepfake_score),
            "deepfake_details": deepfake_details,
            "report_id": report_id,
            "tx_hash": tx_hash
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Deepfake detection failed: {str(e)}")
        return jsonify({"error": f"Deepfake detection failed: {str(e)}"}), 500

@api_bp.route('/fraud/reports', methods=['GET'])
@token_required
def get_fraud_reports_api(current_user):
    """Get fraud reports list"""
    try:
        # Check user permissions (only admin can view all reports)
        if not current_user.get('is_admin', False):
            return jsonify({"error": "No permission to access fraud reports"}), 403
        
        # Get query parameters
        fraud_type = request.args.get('type')
        status = request.args.get('status')
        limit = int(request.args.get('limit', 50))
        
        # Get fraud reports
        reports = get_fraud_reports(
            fraud_type=fraud_type,
            status=status,
            limit=limit
        )
        
        return jsonify({
            "reports": reports,
            "count": len(reports)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Failed to get fraud reports: {str(e)}")
        return jsonify({"error": f"Failed to get fraud reports: {str(e)}"}), 500

@api_bp.route('/fraud/risk-score', methods=['POST'])
def calculate_risk_score():
    """Calculate identity risk score"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('did'):
            return jsonify({"error": "Missing DID"}), 400
        
        did = data.get('did')
        
        # Get fraud report history for this DID
        fraud_history = get_fraud_reports(did=did)
        
        # Calculate base risk score
        base_risk_score = 0.0
        
        # If fraud history exists, increase risk score
        if fraud_history:
            # Calculate risk score based on number and severity of fraud reports
            for report in fraud_history:
                base_risk_score += report.get('score', 0) * 0.1
        
        # Consider other risk factors
        additional_risk = 0.0
        
        # If additional risk assessment data provided
        if data.get('risk_factors'):
            risk_factors = data.get('risk_factors')
            
            # Unusual behavior patterns
            if risk_factors.get('unusual_behavior', False):
                additional_risk += 0.2
            
            # Location mismatch
            if risk_factors.get('location_mismatch', False):
                additional_risk += 0.15
            
            # Device anomaly
            if risk_factors.get('device_anomaly', False):
                additional_risk += 0.1
        
        # Calculate total risk score (max 1.0)
        total_risk_score = min(base_risk_score + additional_risk, 1.0)
        
        # Determine risk level
        risk_level = "Low"
        if total_risk_score >= 0.7:
            risk_level = "High"
        elif total_risk_score >= 0.4:
            risk_level = "Medium"
        
        return jsonify({
            "did": did,
            "risk_score": float(total_risk_score),
            "risk_level": risk_level,
            "fraud_history_count": len(fraud_history)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Risk score calculation failed: {str(e)}")
        return jsonify({"error": f"Risk score calculation failed: {str(e)}"}), 500 