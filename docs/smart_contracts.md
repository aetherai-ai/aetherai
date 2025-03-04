# Decentralized Identity Authentication System Smart Contracts

This document provides examples and documentation for smart contracts used in the Decentralized Identity Authentication System (DID).

## 1. DID Contract

The DID contract is responsible for managing the creation, retrieval, and updating of Decentralized Identity Identifiers (DID).

### 1.1 Contract Code Example (Solidity)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title DIDRegistry
 * @dev Manages Decentralized Identity Identifiers (DID)
 */
contract DIDRegistry {
    // DID document structure
    struct DIDDocument {
        string did;
        string document;
        address owner;
        uint256 created;
        uint256 updated;
        bool active;
    }
    
    // DID mapping: DID identifier => DID document
    mapping(string => DIDDocument) private didDocuments;
    
    // User DID mapping: User address => DID identifier array
    mapping(address => string[]) private userDIDs;
    
    // Events
    event DIDCreated(string did, address owner, uint256 timestamp);
    event DIDUpdated(string did, address owner, uint256 timestamp);
    event DIDDeactivated(string did, address owner, uint256 timestamp);
    
    /**
     * @dev Create new DID
     * @param did DID identifier
     * @param document DID document (JSON string)
     */
    function createDID(string memory did, string memory document) public {
        // Ensure DID doesn't exist
        require(didDocuments[did].created == 0, "DID already exists");
        
        // Create DID document
        didDocuments[did] = DIDDocument({
            did: did,
            document: document,
            owner: msg.sender,
            created: block.timestamp,
            updated: block.timestamp,
            active: true
        });
        
        // Add to user's DID list
        userDIDs[msg.sender].push(did);
        
        // Emit event
        emit DIDCreated(did, msg.sender, block.timestamp);
    }
    
    /**
     * @dev Get DID document
     * @param did DID identifier
     * @return DID document string
     */
    function getDID(string memory did) public view returns (string memory) {
        require(didDocuments[did].created > 0, "DID not found");
        require(didDocuments[did].active, "DID is deactivated");
        return didDocuments[did].document;
    }
    
    /**
     * @dev Update DID document
     * @param did DID identifier
     * @param document New DID document
     */
    function updateDID(string memory did, string memory document) public {
        require(didDocuments[did].created > 0, "DID not found");
        require(didDocuments[did].owner == msg.sender, "Not DID owner");
        require(didDocuments[did].active, "DID is deactivated");
        
        didDocuments[did].document = document;
        didDocuments[did].updated = block.timestamp;
        
        emit DIDUpdated(did, msg.sender, block.timestamp);
    }
    
    /**
     * @dev Deactivate DID
     * @param did DID identifier
     */
    function deactivateDID(string memory did) public {
        require(didDocuments[did].created > 0, "DID not found");
        require(didDocuments[did].owner == msg.sender, "Not DID owner");
        require(didDocuments[did].active, "DID already deactivated");
        
        didDocuments[did].active = false;
        
        emit DIDDeactivated(did, msg.sender, block.timestamp);
    }
}
```

## 2. Biometric Contract

The biometric contract manages storage and verification of biometric feature hashes.

### 2.1 Contract Code Example (Solidity)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title BiometricRegistry
 * @dev Manages biometric feature hashes
 */
contract BiometricRegistry {
    // Biometric data structure
    struct BiometricData {
        string did;
        string biometricType;
        uint256 biometricHash;
        uint256 timestamp;
    }
    
    // Biometric mapping: DID + type => hash
    mapping(string => mapping(string => uint256)) private biometricHashes;
    
    // Events
    event BiometricStored(string did, string biometricType, uint256 timestamp);
    event BiometricUpdated(string did, string biometricType, uint256 timestamp);
    
    /**
     * @dev Store biometric hash
     * @param did DID identifier
     * @param biometricType Biometric type (e.g., "face", "fingerprint")
     * @param biometricHash Hash value of biometric feature
     */
    function storeBiometricHash(
        string memory did,
        string memory biometricType,
        uint256 biometricHash
    ) public {
        biometricHashes[did][biometricType] = biometricHash;
        emit BiometricStored(did, biometricType, block.timestamp);
    }
    
    /**
     * @dev Get biometric hash
     * @param did DID identifier
     * @param biometricType Biometric type
     * @return Biometric hash value
     */
    function getBiometricHash(
        string memory did,
        string memory biometricType
    ) public view returns (uint256) {
        return biometricHashes[did][biometricType];
    }
}
```

## 3. Fraud Detection Contract

The fraud detection contract manages fraud reports and risk scores.

### 3.1 Contract Code Example (Solidity)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title FraudDetection
 * @dev Manages fraud reports and risk scores
 */
contract FraudDetection {
    // Fraud report structure
    struct FraudReport {
        string fraudType;
        uint256 fraudScore;
        string details;
        uint256 timestamp;
    }
    
    // Fraud reports mapping: DID => reports array
    mapping(string => FraudReport[]) private fraudReports;
    
    // Events
    event FraudReported(string did, string fraudType, uint256 timestamp);
    
    /**
     * @dev Report fraud
     * @param did DID identifier
     * @param fraudType Fraud type
     * @param fraudScore Risk score (0-100)
     * @param details Detailed information (JSON string)
     */
    function reportFraud(
        string memory did,
        string memory fraudType,
        uint256 fraudScore,
        string memory details
    ) public {
        require(fraudScore <= 100, "Invalid fraud score");
        
        fraudReports[did].push(FraudReport({
            fraudType: fraudType,
            fraudScore: fraudScore,
            details: details,
            timestamp: block.timestamp
        }));
        
        emit FraudReported(did, fraudType, block.timestamp);
    }
    
    /**
     * @dev Get fraud reports
     * @param did DID identifier
     * @return Array of fraud reports
     */
    function getFraudReports(
        string memory did
    ) public view returns (FraudReport[] memory) {
        return fraudReports[did];
    }
}
```

## 4. Contract Usage Example

Python example for interacting with smart contracts:

```python
from web3 import Web3
import json

# Connect to blockchain
web3 = Web3(Web3.HTTPProvider("http://localhost:8545"))

# Load contract ABI and address
with open("contract_abi.json") as f:
    contract_abi = json.load(f)

contract_address = "0x1234567890123456789012345678901234567890"
private_key = "your-private-key"

# Create contract instance
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Create DID
did_id = "did:example:123456789abcdefghi"
document = '{"id": "did:example:123456789abcdefghi", "name": "John Doe"}'
tx_hash = create_did(contract, did_id, document, private_key)
print(f"Transaction hash: {tx_hash}")

# Get DID document
did_doc = get_did(contract, did_id)
print(f"DID document: {did_doc}")

# Store biometric hash
biometric_type = "face"
biometric_hash = 12345678901234567890  # Should be a hash value in real application
tx_hash = store_biometric_hash(biometric_contract, did_id, biometric_type, biometric_hash, private_key)
print(f"Biometric storage transaction hash: {tx_hash}")

# Verify biometric hash
is_valid = verify_biometric_hash(biometric_contract, did_id, biometric_type, biometric_hash)
print(f"Biometric verification result: {is_valid}")

# Report fraud
fraud_type = "identity"
fraud_score = 85  # 0-100
details = '{"risk_factors":["Invalid ID number format"]}'
tx_hash = report_fraud(fraud_contract, did_id, fraud_type, fraud_score, details, private_key)
print(f"Fraud report transaction hash: {tx_hash}")

# Get fraud reports
reports = get_fraud_reports(fraud_contract, did_id)
print(f"Fraud reports: {reports}")
```

## 5. Security Considerations

When using smart contracts, please note the following security considerations:

1. **Private Key Protection**: Ensure secure storage of private keys, never hardcode them in the code
2. **Contract Audit**: Conduct security audit before deploying contracts
3. **Access Control**: Ensure only authorized users can execute sensitive operations
4. **Data Privacy**: Don't store sensitive personal data on blockchain, only store hash values
5. **Gas Optimization**: Optimize contracts to reduce Gas consumption
6. **Error Handling**: Handle errors and exceptions properly in contracts
7. **Version Control**: Use stable versions of the Solidity compiler
8. **Test Network**: Test thoroughly on test networks before deploying to mainnet

## 6. Future Improvements

Consider the following improvements for future development:

1. **Multi-signature Control**: Add multi-signature mechanism to enhance security
2. **Proxy Contracts**: Use proxy contract pattern for contract upgrades
3. **Zero-knowledge Proofs**: Integrate zero-knowledge proof technology for privacy protection
4. **Cross-chain Support**: Support identity verification across multiple blockchain networks
5. **Decentralized Storage**: Integrate IPFS and other decentralized storage systems
6. **ERC Standards**: Follow relevant ERC standards (e.g., ERC-725/ERC-735) 