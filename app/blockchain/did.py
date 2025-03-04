#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Blockchain DID Interaction Module
"""

import os
import json
import logging
from web3 import Web3
from eth_account import Account

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_web3_connection():
    """Get Web3 connection"""
    provider_url = os.getenv("BLOCKCHAIN_PROVIDER_URL", "http://localhost:8545")
    web3 = Web3(Web3.HTTPProvider(provider_url))
    return web3

# DID contract ABI (simplified)
DID_CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "did", "type": "string"},
            {"internalType": "string", "name": "document", "type": "string"}
        ],
        "name": "createDID",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "did", "type": "string"}
        ],
        "name": "getDID",
        "outputs": [
            {"internalType": "string", "name": "", "type": "string"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "did", "type": "string"},
            {"internalType": "string", "name": "document", "type": "string"}
        ],
        "name": "updateDID",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

def get_contract():
    """Get DID contract instance"""
    web3 = get_web3_connection()
    contract_address = os.getenv("CONTRACT_ADDRESS")
    
    # Check if contract address is valid
    if not contract_address or not web3.is_address(contract_address):
        logger.error("Invalid contract address")
        return None
    
    # Create contract instance
    contract = web3.eth.contract(address=contract_address, abi=DID_CONTRACT_ABI)
    return contract

def get_account():
    """Get blockchain account"""
    web3 = get_web3_connection()
    private_key = os.getenv("WALLET_PRIVATE_KEY")
    
    if not private_key:
        logger.error("Wallet private key not configured")
        return None
    
    account = Account.from_key(private_key)
    return account

def create_did(did_id, document):
    """Create DID"""
    try:
        web3 = get_web3_connection()
        contract = get_contract()
        account = get_account()
        
        if not contract or not account:
            logger.error("Contract or account initialization failed")
            return None
        
        # Build transaction
        tx = contract.functions.createDID(did_id, document).build_transaction({
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
        logger.error(f"Failed to create DID: {str(e)}")
        return None

def verify_did(did_id, document=None, return_doc=False):
    """Verify DID"""
    try:
        contract = get_contract()
        
        if not contract:
            logger.error("Contract initialization failed")
            return False if not return_doc else None
        
        # Get DID document from blockchain
        blockchain_document = contract.functions.getDID(did_id).call()
        
        if not blockchain_document:
            logger.error(f"DID not found: {did_id}")
            return False if not return_doc else None
        
        # If document return is requested
        if return_doc:
            return json.loads(blockchain_document)
        
        # If document is provided, verify if it matches
        if document:
            # Parse JSON documents
            doc_obj = json.loads(document)
            blockchain_doc_obj = json.loads(blockchain_document)
            
            # Compare ID fields
            if doc_obj.get("id") != blockchain_doc_obj.get("id"):
                return False
            
            # Compare public key fields
            if doc_obj.get("publicKey") != blockchain_doc_obj.get("publicKey"):
                return False
            
            return True
        
        # If no document provided, only verify DID existence
        return True
        
    except Exception as e:
        logger.error(f"Failed to verify DID: {str(e)}")
        return False if not return_doc else None

def update_did(did_id, document):
    """Update DID"""
    try:
        web3 = get_web3_connection()
        contract = get_contract()
        account = get_account()
        
        if not contract or not account:
            logger.error("Contract or account initialization failed")
            return None
        
        # Build transaction
        tx = contract.functions.updateDID(did_id, document).build_transaction({
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
        logger.error(f"Failed to update DID: {str(e)}")
        return None 