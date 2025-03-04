#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cryptography Utility Module
"""

import os
import base64
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def generate_key_pair():
    """Generate RSA key pair"""
    key = RSA.generate(2048)
    private_key = key.export_key().decode('utf-8')
    public_key = key.publickey().export_key().decode('utf-8')
    return private_key, public_key

def sign_message(private_key_str, message):
    """Sign message with private key"""
    try:
        # Load private key
        private_key = RSA.import_key(private_key_str)
        
        # Calculate message hash
        h = SHA256.new(message.encode('utf-8'))
        
        # Sign
        signature = pkcs1_15.new(private_key).sign(h)
        
        # Return Base64 encoded signature
        return base64.b64encode(signature).decode('utf-8')
    except Exception as e:
        print(f"Signing failed: {str(e)}")
        return None

def verify_signature(public_key_str, message, signature_base64):
    """Verify signature"""
    try:
        # Load public key
        public_key = RSA.import_key(public_key_str)
        
        # Calculate message hash
        h = SHA256.new(message.encode('utf-8'))
        
        # Decode signature
        signature = base64.b64decode(signature_base64)
        
        # Verify signature
        pkcs1_15.new(public_key).verify(h, signature)
        return True
    except Exception as e:
        print(f"Signature verification failed: {str(e)}")
        return False

def encrypt_data(data, key=None):
    """Encrypt data"""
    try:
        # If no key provided, use key from environment variable
        if key is None:
            key = os.getenv("ENCRYPTION_KEY", "default-encryption-key")
        
        # Ensure key length is 32 bytes (256 bits)
        key_bytes = hashlib.sha256(key.encode('utf-8')).digest()
        
        # Generate random initialization vector
        iv = os.urandom(16)
        
        # Create AES encryptor
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        
        # Encrypt data
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Pad data
        padded_data = pad(data, AES.block_size)
        
        # Encrypt
        encrypted_data = cipher.encrypt(padded_data)
        
        # Combine IV and encrypted data
        result = iv + encrypted_data
        
        # Return Base64 encoded result
        return base64.b64encode(result).decode('utf-8')
    except Exception as e:
        print(f"Encryption failed: {str(e)}")
        return None

def decrypt_data(encrypted_data_base64, key=None):
    """Decrypt data"""
    try:
        # If no key provided, use key from environment variable
        if key is None:
            key = os.getenv("ENCRYPTION_KEY", "default-encryption-key")
        
        # Ensure key length is 32 bytes (256 bits)
        key_bytes = hashlib.sha256(key.encode('utf-8')).digest()
        
        # Decode Base64 data
        encrypted_data = base64.b64decode(encrypted_data_base64)
        
        # Extract IV (first 16 bytes)
        iv = encrypted_data[:16]
        
        # Extract encrypted data
        encrypted_data = encrypted_data[16:]
        
        # Create AES decryptor
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        
        # Decrypt data
        decrypted_data = cipher.decrypt(encrypted_data)
        
        # Remove padding
        unpadded_data = unpad(decrypted_data, AES.block_size)
        
        # Return decrypted data
        return unpadded_data
    except Exception as e:
        print(f"Decryption failed: {str(e)}")
        return None

def hash_data(data):
    """Calculate hash value of data"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    # Calculate hash using SHA-256
    hash_obj = hashlib.sha256(data)
    return hash_obj.hexdigest() 