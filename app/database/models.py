#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Database Models Module
"""

import os
import uuid
import datetime
import pymongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

# 连接到MongoDB
def get_db_connection():
    """Get database connection"""
    client = pymongo.MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/did_system"))
    db = client.get_default_database()
    return db

# 用户相关操作
def create_user(user_data):
    """Create new user"""
    db = get_db_connection()
    
    # Hash password
    user_data["password"] = generate_password_hash(user_data["password"])
    
    # Add creation timestamp
    if "created_at" not in user_data:
        user_data["created_at"] = datetime.datetime.utcnow()
    
    # Insert user data
    result = db.users.insert_one(user_data)
    
    return str(result.inserted_id)

def get_user_by_did(did):
    """Get user by DID"""
    db = get_db_connection()
    user = db.users.find_one({"did": did})
    return user

def get_user_by_username(username):
    """Get user by username"""
    db = get_db_connection()
    user = db.users.find_one({"username": username})
    return user

def verify_user_credentials(did=None, username=None, password=None):
    """Verify user credentials"""
    db = get_db_connection()
    
    # Query conditions
    query = {}
    if did:
        query["did"] = did
    elif username:
        query["username"] = username
    else:
        return None
    
    # Query user
    user = db.users.find_one(query)
    
    if not user:
        return None
    
    # Verify password
    if not check_password_hash(user["password"], password):
        return None
    
    # Convert ObjectId to string
    if "_id" in user:
        user["id"] = str(user["_id"])
    
    return user

# 身份相关操作
def save_identity(identity_data):
    """Save identity information"""
    db = get_db_connection()
    
    # Add creation timestamp
    if "created_at" not in identity_data:
        identity_data["created_at"] = datetime.datetime.utcnow()
    
    # Update or insert
    result = db.identities.update_one(
        {"did": identity_data["did"]},
        {"$set": identity_data},
        upsert=True
    )
    
    return str(result.upserted_id) if result.upserted_id else None

def get_identity(did):
    """Get identity by DID"""
    db = get_db_connection()
    identity = db.identities.find_one({"did": did})
    
    # Convert ObjectId to string
    if identity and "_id" in identity:
        identity["_id"] = str(identity["_id"])
    
    return identity

def list_identities(owner_id=None, status=None, limit=50):
    """List identities"""
    db = get_db_connection()
    
    # Build query conditions
    query = {}
    if owner_id:
        query["owner"] = owner_id
    if status:
        query["status"] = status
    
    # Query identities
    identities = list(db.identities.find(query).limit(limit))
    
    # Convert ObjectId to string
    for identity in identities:
        if "_id" in identity:
            identity["_id"] = str(identity["_id"])
    
    return identities

# 生物特征相关操作
def save_biometric_data(biometric_data):
    """Save biometric data"""
    db = get_db_connection()
    
    # Add creation timestamp
    if "created_at" not in biometric_data:
        biometric_data["created_at"] = datetime.datetime.utcnow()
    
    # Check if record exists
    existing = db.biometrics.find_one({
        "user_id": biometric_data["user_id"],
        "type": biometric_data["type"]
    })
    
    if existing:
        # Update existing record
        db.biometrics.update_one(
            {"_id": existing["_id"]},
            {"$set": biometric_data}
        )
        return str(existing["_id"])
    else:
        # Insert new record
        result = db.biometrics.insert_one(biometric_data)
        return str(result.inserted_id)

def get_user_biometrics(did, biometric_type):
    """Get user biometric data"""
    db = get_db_connection()
    
    # Get user first
    user = get_user_by_did(did)
    if not user:
        return None
    
    # Query biometrics
    biometric = db.biometrics.find_one({
        "user_id": str(user["_id"]),
        "type": biometric_type
    })
    
    # Convert ObjectId to string
    if biometric and "_id" in biometric:
        biometric["_id"] = str(biometric["_id"])
    
    return biometric

# 欺诈报告相关操作
def save_fraud_report(report_data):
    """Save fraud report"""
    db = get_db_connection()
    
    # Add creation timestamp
    if "timestamp" not in report_data:
        report_data["timestamp"] = datetime.datetime.utcnow()
    
    # Insert report
    result = db.fraud_reports.insert_one(report_data)
    return str(result.inserted_id)

def get_fraud_reports(did=None, fraud_type=None, status=None, limit=50):
    """Get fraud reports"""
    db = get_db_connection()
    
    # Build query conditions
    query = {}
    if did:
        query["did"] = did
    if fraud_type:
        query["type"] = fraud_type
    if status:
        query["status"] = status
    
    # Query reports
    reports = list(db.fraud_reports.find(query).sort("timestamp", -1).limit(limit))
    
    # Convert ObjectId to string and format timestamp
    for report in reports:
        if "_id" in report:
            report["_id"] = str(report["_id"])
        if "timestamp" in report:
            report["timestamp"] = report["timestamp"].isoformat()
    
    return reports 