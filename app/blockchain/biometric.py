#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Biometric Blockchain Interaction Module
"""

import os
import json
import logging
from web3 import Web3
from eth_account import Account
from app.blockchain.did import get_web3_connection, get_account

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Biometric contract ABI (simplified)
BIOMETRIC_CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "did", "type": "string"},
            {"internalType": "string", "name": "biometricType", "type": "string"},
            {"internalType": "uint256", "name": "biometricHash", "type": "uint256"}
        ],
        "name": "storeBiometricHash",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "did", "type": "string"},
            {"internalType": "string", "name": "biometricType", "type": "string"}
        ],
        "name": "getBiometricHash",
        "outputs": [
            {"internalType": "uint256", "name": "", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

def get_biometric_contract():
    """Get biometric contract instance"""
    web3 = get_web3_connection()
    contract_address = os.getenv("BIOMETRIC_CONTRACT_ADDRESS", os.getenv("CONTRACT_ADDRESS"))
    
    # Check if contract address is valid
    if not contract_address or not web3.is_address(contract_address):
        logger.error("Invalid biometric contract address")
        return None
    
    # Create contract instance
    contract = web3.eth.contract(address=contract_address, abi=BIOMETRIC_CONTRACT_ABI)
    return contract

def store_biometric_hash(did, biometric_type, biometric_hash):
    """Store biometric feature hash to blockchain"""
    try:
        web3 = get_web3_connection()
        contract = get_biometric_contract()
        account = get_account()
        
        if not contract or not account:
            logger.error("Contract or account initialization failed")
            return None
        
        # Build transaction
        tx = contract.functions.storeBiometricHash(
            did, 
            biometric_type, 
            int(biometric_hash)
        ).build_transaction({
            'from': account.address,
            'nonce': web3.eth.get_transaction_count(account.address),
            'gas': 2000000,
            'gasPrice': web3.eth.gas_price
        })
        
        # Sign transaction
        signed_tx = web3.eth.account.sign_transaction(tx, private_key=os.getenv("WALLET_PRIVATE_KEY"))
        
        # Send transaction
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # Wait for transaction confirmation
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        
        return tx_receipt.transactionHash.hex()
        
    except Exception as e:
        logger.error(f"Failed to store biometric hash: {str(e)}")
        return None

def verify_biometric_hash(did, biometric_type, biometric_hash):
    """Verify biometric feature hash"""
    try:
        contract = get_biometric_contract()
        
        if not contract:
            logger.error("Contract initialization failed")
            return False
        
        # Get biometric hash from blockchain
        blockchain_hash = contract.functions.getBiometricHash(did, biometric_type).call()
        
        if not blockchain_hash:
            logger.error(f"Biometric hash not found: {did}, {biometric_type}")
            return False
        
        # Compare hash values
        return int(biometric_hash) == blockchain_hash
        
    except Exception as e:
        logger.error(f"Failed to verify biometric hash: {str(e)}")
        return False 