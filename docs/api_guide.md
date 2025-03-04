# Decentralized Identity Authentication System API Guide

This document provides API documentation and examples for the Decentralized Identity (DID) Authentication System.

## Basic Information

- **Base URL**: `http://localhost:5000/api`
- **Content Type**: All requests and responses use JSON format
- **Authentication**: Most APIs require JWT token authentication, add `Authorization: Bearer <token>` in request header

## 1. Identity Management API

### 1.1 Create DID Identity

Create a new Decentralized Identity Identifier (DID).

- **URL**: `/identity`
- **Method**: `POST`
- **Authentication**: Not required

**Request Parameters**:

```json
{
  "name": "John Doe",
  "public_key": "public key string",
  "created": "2023-01-01T00:00:00Z",
  "owner": "user ID (optional)"
}
```

**Response Example**:

```json
{
  "success": true,
  "did": "did:example:123456789abcdefghi",
  "tx_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
  "identity_id": "60f1a5c3e4b0f1234567890a"
}
```

### 1.2 Get DID Identity Information

Get identity information for a specific DID.

- **URL**: `/identity/<did_id>`
- **Method**: `GET`
- **Authentication**: Not required

**Response Example**:

```json
{
  "identity": {
    "_id": "60f1a5c3e4b0f1234567890a",
    "did": "did:example:123456789abcdefghi",
    "document": {
      "id": "did:example:123456789abcdefghi",
      "name": "John Doe",
      "publicKey": "public key string",
      "created": "2023-01-01T00:00:00Z",
      "authentication": [
        {
          "type": "Ed25519VerificationKey2020",
          "publicKeyMultibase": "public key string"
        }
      ]
    },
    "tx_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
    "owner": "user ID",
    "status": "active"
  },
  "verified": true
}
```

### 1.3 Get All User Identities

Get all DID identities for the current user.

- **URL**: `/identity`
- **Method**: `GET`
- **Authentication**: Requires JWT token

**Response Example**:

```json
{
  "identities": [
    {
      "_id": "60f1a5c3e4b0f1234567890a",
      "did": "did:example:123456789abcdefghi",
      "document": {
        "id": "did:example:123456789abcdefghi",
        "name": "John Doe",
        "publicKey": "public key string",
        "created": "2023-01-01T00:00:00Z",
        "authentication": [
          {
            "type": "Ed25519VerificationKey2020",
            "publicKeyMultibase": "public key string"
          }
        ]
      },
      "tx_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
      "owner": "user ID",
      "status": "active"
    }
  ],
  "count": 1
}
```

### 1.4 Update DID Identity Information

Update identity information for a specific DID.

- **URL**: `/identity/<did_id>`
- **Method**: `PUT`
- **Authentication**: Requires JWT token

**Request Parameters**:

```json
{
  "name": "John Doe (updated)",
  "public_key": "new public key string (optional)"
}
```

**Response Example**:

```json
{
  "success": true,
  "did": "did:example:123456789abcdefghi",
  "tx_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
}
```

## 2. Authentication API

### 2.1 User Registration

Register a new user.

- **URL**: `/auth/register`
- **Method**: `POST`
- **Authentication**: Not required

**Request Parameters**:

```json
{
  "did": "did:example:123456789abcdefghi",
  "username": "johndoe",
  "password": "password123",
  "email": "johndoe@example.com"
}
```

**Response Example**:

```json
{
  "success": true,
  "message": "User registration successful",
  "user_id": "60f1a5c3e4b0f1234567890b"
}
```

### 2.2 User Login

User login with username/DID and password.

- **URL**: `/auth/login`
- **Method**: `POST`
- **Authentication**: Not required

**Request Parameters**:

```json
{
  "username": "johndoe",
  "password": "password123"
}
```

or

```json
{
  "did": "did:example:123456789abcdefghi",
  "password": "password123"
}
```

**Response Example**:

```json
{
  "success": true,
  "token": "JWT_TOKEN_STRING",
  "user": {
    "id": "60f1a5c3e4b0f1234567890b",
    "username": "johndoe",
    "did": "did:example:123456789abcdefghi",
    "email": "johndoe@example.com"
  }
}
```

### 2.3 Verify Signature

Verify digital signature.

- **URL**: `/auth/verify-signature`
- **Method**: `POST`
- **Authentication**: Not required

**Request Parameters**:

```json
{
  "did": "did:example:123456789abcdefghi",
  "message": "Message to be signed",
  "signature": "Digital signature string"
}
```

**Response Example**:

```json
{
  "valid": true,
  "did": "did:example:123456789abcdefghi"
}
```

## 3. Biometric API

### 3.1 Register Facial Biometrics

Register user's facial biometric features.

- **URL**: `/biometric/register/face`
- **Method**: `POST`
- **Authentication**: Requires JWT token

**Request Parameters**:

```json
{
  "face_image": "Base64 encoded facial image"
}
```

**Response Example**:

```json
{
  "success": true,
  "message": "Facial biometric registration successful",
  "biometric_id": "60f1a5c3e4b0f1234567890c",
  "tx_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
}
```

### 3.2 Verify Facial Biometrics

Verify user's facial biometric features.

- **URL**: `/biometric/verify/face`
- **Method**: `POST`
- **Authentication**: Not required

**Request Parameters**:

```json
{
  "face_image": "Base64 encoded facial image",
  "did": "did:example:123456789abcdefghi"
}
```

**Response Example**:

```json
{
  "verified": true,
  "confidence": 0.95,
  "threshold": 0.6,
  "blockchain_verified": true
}
```

### 3.3 Register Fingerprint Biometrics

Register user's fingerprint biometric features.

- **URL**: `/biometric/register/fingerprint`
- **Method**: `POST`
- **Authentication**: Requires JWT token

**Request Parameters**:

```json
{
  "fingerprint_data": "Base64 encoded fingerprint data"
}
```

**Response Example**:

```json
{
  "success": true,
  "message": "Fingerprint registration successful",
  "biometric_id": "60f1a5c3e4b0f1234567890d",
  "tx_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
}
```

## 4. Fraud Detection API

### 4.1 Detect Identity Fraud

Perform identity fraud detection.

- **URL**: `/fraud/detect/identity`
- **Method**: `POST`
- **Authentication**: Not required

**Request Parameters**:

```json
{
  "identity_data": {
    "did": "did:example:123456789abcdefghi",
    "document_type": "id_card",
    "document_number": "ID12345678",
    "name": "John Doe",
    "birth_date": "1990-01-01"
  }
}
```

**Response Example**:

```json
{
  "is_fraud": false,
  "fraud_score": 0.05,
  "risk_level": "Low",
  "details": {
    "risk_factors": [],
    "timestamp": "2023-01-01T00:00:00Z"
  }
}
```

### 4.2 Calculate Risk Score

Calculate risk score for a DID.

- **URL**: `/fraud/risk-score`
- **Method**: `POST`
- **Authentication**: Not required

**Request Parameters**:

```json
{
  "did": "did:example:123456789abcdefghi",
  "risk_factors": {
    "unusual_behavior": false,
    "location_mismatch": false,
    "device_anomaly": false
  }
}
```

**Response Example**:

```json
{
  "did": "did:example:123456789abcdefghi",
  "risk_score": 0.1,
  "risk_level": "Low",
  "fraud_history_count": 0
}
```

## Error Responses

All APIs will return appropriate HTTP status codes and error messages when errors occur.

**Error Response Example**:

```json
{
  "error": "Error message description"
}
```

Common HTTP Status Codes:
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Not authenticated or authentication failed
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server internal error

## Code Examples

### Python Example

```python
import requests
import json
import base64

# Base URL
BASE_URL = "http://localhost:5000/api"

# User login
def login(username, password):
    url = f"{BASE_URL}/auth/login"
    payload = {
        "username": username,
        "password": password
    }
    response = requests.post(url, json=payload)
    return response.json()

# Create DID identity
def create_identity(name, public_key):
    url = f"{BASE_URL}/identity"
    payload = {
        "name": name,
        "public_key": public_key,
        "created": "2023-01-01T00:00:00Z"
    }
    response = requests.post(url, json=payload)
    return response.json()

# Verify facial biometrics
def verify_face(face_image_path, did):
    url = f"{BASE_URL}/biometric/verify/face"
    
    # Read image file and convert to Base64
    with open(face_image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    
    payload = {
        "face_image": encoded_string,
        "did": did
    }
    response = requests.post(url, json=payload)
    return response.json()

# Usage example
if __name__ == "__main__":
    # Login
    login_result = login("johndoe", "password123")
    token = login_result.get("token")
    
    # Request headers with authentication token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Get all user identities
    identities_url = f"{BASE_URL}/identity"
    identities_response = requests.get(identities_url, headers=headers)
    print(json.dumps(identities_response.json(), indent=4))
``` 