# Aetherai

A decentralized identity authentication system based on blockchain technology and artificial intelligence, providing a secure and privacy-protected identity management solution.

## Project Overview

This project implements a complete decentralized identity authentication system, leveraging the decentralization features of blockchain technology and the intelligent recognition capabilities of AI technology to offer secure and reliable identity management and verification services to users. The system supports biometric identity verification and fraud detection, enhancing security while protecting user data privacy.

## Main Features

### 1. Decentralized Identity (DID)

- Creation and management of decentralized identity identifiers
- Identity claims and verification based on blockchain technology
- Complete control over personal data by users
- Identity information update and management

### 2. Biometric Identity Verification

- Facial recognition for registration and verification
- Fingerprint verification for registration and verification
- Liveness detection to prevent photo attacks
- Secure storage and processing of biometric data

### 3. Fraud Detection

- AI-based identification of fake identities
- Deepfake detection
- Detection of abnormal behavior and risk assessment
- Real-time fraud monitoring and alert system

## Technical Architecture

### Backend Architecture

- **Web Framework**: Flask RESTful API
- **Database**: MongoDB
- **Blockchain**: Ethereum/Web3
- **AI Models**: TensorFlow, OpenCV, face_recognition

### System Layers

1. **API Layer**: RESTful interfaces for handling client requests
2. **Business Logic Layer**: Identity management, authentication, biometric verification, and fraud detection
3. **Blockchain Interaction Layer**: Interaction with blockchain networks for storing and verifying data
4. **AI Model Layer**: Provision of facial recognition, fingerprint recognition, and fraud detection features
5. **Data Storage Layer**: Secure storage of user data and biometric information

## Installation Guide

### Prerequisites

- Python 3.8+
- MongoDB
- Ethereum node or Infura account

### Installation Steps

1. Clone the repository

```bash
git clone https://github.com/aetherai-ai/aetherai.git
cd did-system
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Configure environment variables

```bash
cp .env.example .env
# Edit .env file to include necessary configuration information
```

4. Run the application

```bash
python run.py
```

## API Interface Documentation

### Identity Management API

- `POST /api/identity`: Create a new DID identity
- `GET /api/identity/<did_id>`: Get information for a specific DID identity
- `GET /api/identity`: Get all identities for a user
- `PUT /api/identity/<did_id>`: Update identity information

### Authentication API

- `POST /api/auth/register`: User registration
- `POST /api/auth/login`: User login
- `POST /api/auth/verify-signature`: Verify DID signature

### Biometric Authentication API

- `POST /api/biometric/register/face`: Register facial biometric information
- `POST /api/biometric/verify/face`: Verify facial biometric information
- `POST /api/biometric/register/fingerprint`: Register fingerprint biometric information
- `POST /api/biometric/verify/fingerprint`: Verify fingerprint biometric information

### Fraud Detection API

- `POST /api/fraud/detect/identity`: Detect identity fraud
- `POST /api/fraud/detect/deepfake`: Detect deepfakes
- `GET /api/fraud/reports`: Get a list of fraud reports
- `POST /api/fraud/risk-score`: Calculate identity risk score

## Usage Examples

### Creating a DID Identity

```python
import requests
import json

url = "http://localhost:5000/api/identity"
payload = {
    "name": "Zhang San",
    "public_key": "public key string",
    "created": "2023-01-01T00:00:00Z"
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)
print(json.dumps(response.json(), indent=4))
```

### Facial Recognition Verification

```python
import requests
import json
import base64

# Read image file and convert to Base64
with open("face.jpg", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

url = "http://localhost:5000/api/biometric/verify/face"
payload = {
    "face_image": encoded_string,
    "did": "did:example:123456789abcdefghi"
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)
print(json.dumps(response.json(), indent=4))
```

For more API usage examples, please refer to the `docs/` directory.

## Security Considerations

1. **Data Encryption**: All sensitive data should be encrypted during transmission and storage
2. **Private Key Protection**: Ensure blockchain private keys are securely stored and not hard-coded in the code
3. **API Security**: Use HTTPS and appropriate authentication mechanisms in production environments
4. **Biometric Data Protection**: Store only the hash values of biometric data instead of the raw data

## Development Guide

### Project Structure

```
did-system/
├── app/                    # Application main directory
│   ├── api/                # API interfaces
│   ├── ai/                 # AI models
│   ├── blockchain/         # Blockchain interaction
│   ├── database/           # Database operations
│   ├── utils/              # Utility functions
│   └── __init__.py         # Application initialization
├── models/                 # AI model files
├── docs/                   # Documentation
├── tests/                  # Tests
├── .env.example            # Environment variable example
├── requirements.txt        # Dependency list
├── run.py                  # Application entry point
└── README.md               # Project description
```

### Extension Guide

1. **Add new biometric methods**: Create new modules in the `app/ai/` directory
2. **Integrate other blockchains**: Modify the implementations in the `app/blockchain/` directory
3. **Enhance fraud detection**: Add new detection algorithms in `app/ai/fraud_detection.py`

## Contribution Guide

1. Fork the project
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For any questions or suggestions, please contact us via:

- [GitHub](https://github.com/aetherai-ai/aetherai)
- [Twitter](https://x.com/AetherAi_fun)
