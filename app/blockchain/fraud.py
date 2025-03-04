#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Fraud Detection Blockchain Interaction Module
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

# Fraud detection contract ABI (simplified)
FRAUD_CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "did", "type": "string"},
            {"internalType": "string", "name": "fraudType", "type": "string"},
            {"internalType": "uint256", "name": "fraudScore", "type": "uint256"},
            {"internalType": "string", "name": "details", "type": "string"}
        ],
        "name": "reportFraud",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "did", "type": "string"}
        ],
        "name": "getFraudReports",
        "outputs": [
            {
                "components": [
                    {"internalType": "string", "name": "fraudType", "type": "string"},
                    {"internalType": "uint256", "name": "fraudScore", "type": "uint256"},
                    {"internalType": "string", "name": "details", "type": "string"},
                    {"internalType": "uint256", "name": "timestamp", "type": "uint256"}
                ],
                "internalType": "struct FraudDetection.FraudReport[]",
                "name": "",
                "type": "tuple[]"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

def get_fraud_contract():
    """Get fraud detection contract instance"""
    web3 = get_web3_connection()
    contract_address = os.getenv("FRAUD_CONTRACT_ADDRESS", os.getenv("CONTRACT_ADDRESS"))
    
    # Check if contract address is valid
    if not contract_address or not web3.is_address(contract_address):
        logger.error("Invalid fraud detection contract address")
        return None
    
    # Create contract instance
    contract = web3.eth.contract(address=contract_address, abi=FRAUD_CONTRACT_ABI)
    return contract

def report_fraud_to_blockchain(did, fraud_type, fraud_score, details):
    """Report fraud to blockchain"""
    try:
        web3 = get_web3_connection()
        contract = get_fraud_contract()
        account = get_account()
        
        if not contract or not account:
            logger.error("Contract or account initialization failed")
            return None
        
        # Build transaction
        tx = contract.functions.reportFraud(
            did,
            fraud_type,
            int(fraud_score * 100),  # Convert to integer (percentage)
            details
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
        logger.error(f"Failed to report fraud: {str(e)}")
        return None

def get_fraud_reports_from_blockchain(did):
    """Get fraud reports from blockchain"""
    try:
        contract = get_fraud_contract()
        
        if not contract:
            logger.error("Contract initialization failed")
            return []
        
        # Get fraud reports from blockchain
        reports = contract.functions.getFraudReports(did).call()
        
        # Format reports
        formatted_reports = []
        for report in reports:
            formatted_reports.append({
                "fraud_type": report[0],
                "fraud_score": report[1] / 100,  # Convert back to decimal
                "details": json.loads(report[2]) if report[2] else {},
                "timestamp": report[3]
            })
        
        return formatted_reports
        
    except Exception as e:
        logger.error(f"Failed to get fraud reports: {str(e)}")
        return [] 