# SecureLink – Hybrid Cryptography-Based Secure File Transfer System

**Subject:** Data Network Security (DNS) &bull; Academic Mini-Project  
**Domain:** Applied Cryptography, Network Security, Authenticated File Exchange  
**Target Level:** B.Tech / B.E. Computer Science & Engineering  

---

## 1. Project Overview

**SecureLink** is a defense-in-depth secure file transfer web application engineered to protect sensitive files against passive eavesdropping, active Man-in-the-Middle (MITM) tampering, unauthorized decryption, and server-side data exposure.

The core innovation of SecureLink is its **Hybrid Cryptography Architecture**:
1. **Symmetric Encryption (Bulk Cipher):** Uses **AES-256-GCM** (Galois/Counter Mode) with cryptographically random 96-bit nonces to encrypt arbitrary files at hardware speed, generating a 128-bit GHASH authentication tag.
2. **Asymmetric Key Encapsulation (KEM):** Uses **RSA-3072** with **OAEP** (Optimal Asymmetric Encryption Padding) and SHA-256 MGF1 to encrypt the ephemeral 256-bit AES session key using the recipient's public key.
3. **Dual-Layer Integrity Verification:** Compares the pre-encryption **SHA-256** plaintext digest with the post-decryption digest using constant-time comparison (`hmac.compare_digest`), backed by the hardware-level AES-GCM GHASH tag.
4. **Zero-Plaintext Server Policy:** The server disk only ever stores high-entropy ciphertext files (`.enc`). Unencrypted plaintext and raw AES session keys are purged immediately from memory after dispatch.
5. **Private Key Protection at Rest:** User RSA private keys are encrypted using **PKCS#8** with `BestAvailableEncryption` (AES-256-CBC) derived from each user's master password.

---

## 2. Cryptographic Specifications

| Component | Standard / Algorithm | Key / Parameter Size | Security Function |
| :--- | :--- | :--- | :--- |
| **Bulk Symmetric Cipher** | AES-GCM (NIST SP 800-38D) | 256-bit Key, 96-bit Nonce | High-speed bulk payload confidentiality |
| **Authentication Tag** | GHASH over GF(2^128) | 128-bit (16 bytes) | Authenticated Encryption with Associated Data (AEAD) |
| **Asymmetric Key Exchange** | RSA-OAEP (RFC 8017 / PKCS#1 v2.2) | 3072-bit Modulus ($e=65537$) | IND-CCA2 secure session key encapsulation |
| **Mask Generation Function** | MGF1 with SHA-256 | SHA-256 (256 bits) | Padding entropy & chosen-ciphertext defense |
| **Data Integrity Verification** | SHA-256 (FIPS PUB 180-4) | 256-bit Hexadecimal Digest | Pre/Post-transmission bit-level integrity verification |
| **Private Key At-Rest Protection**| PKCS#8 (RFC 5208) | PBKDF2 / AES-256-CBC | Encrypts private key in DB using user master password |
| **User Password Hashing** | Werkzeug (scrypt / PBKDF2:SHA-256) | Salted, Multi-iteration | Mitigates offline credential dictionary attacks |

---

## 3. System Architecture & Workflow

```
[ Sender (Alice) ]
       │
       ├─► 1. Compute SHA-256(Plaintext) ──────────────────────────► (Stored in DB)
       │
       ├─► 2. Generate CSPRNG Ephemeral 256-bit AES Key + 96-bit Nonce
       │
       ├─► 3. AES-256-GCM Encrypt(Plaintext, Nonce, Filename) ─────► Storage: storage/encrypted/*.enc
       │                                                             (Ciphertext + 128-bit Tag)
       │
       └─► 4. RSA-OAEP Encrypt(AES Key, Bob's Public Key) ─────────► (Stored in DB transfers)
                                                                            │
────────────────────────────────────────────────────────────────────────────┼───────────────────────────
                                                                            ▼
                                                                  [ Receiver (Bob) ]
                                                                            │
       ┌─◄ 5. Supply Master Password to unlock PKCS#8 Private Key ◄─────────┤
       │
       ├─► 6. RSA-OAEP Decrypt(Wrapped AES Key) -> Recover 256-bit AES Key
       │
       ├─► 7. AES-256-GCM Decrypt(Ciphertext, Nonce, Tag, Filename)
       │         └─► [Pass] -> Plaintext Extracted
       │         └─► [Fail] -> InvalidTag Exception (Tamper Blocked!)
       │
       └─► 8. Compute SHA-256(Recovered Plaintext) == Pre-Hash?
                 └─► [Match: YES] -> Bit-for-bit Integrity Verified!
```

---

## 4. Project Directory Structure

```
SecureLink/
├── app.py                     # Flask application factory, routes registration, security headers
├── config.py                  # Application configuration, cryptographic parameters, upload limits
├── requirements.txt           # Python dependency requirements
├── README.md                  # Comprehensive documentation, setup, and testing guide
├── .gitignore                 # Git ignore rules for database, venv, and cache
│
├── crypto/                    # Cryptographic Engine
│   ├── aes.py                 # AES-256-GCM authenticated encryption and decryption
│   ├── rsa.py                 # RSA-3072 key pair generation, OAEP wrapping, PKCS#8 serialization
│   └── hashing.py             # SHA-256 chunked hashing, constant-time compare, password hashing
│
├── database/                  # Relational Database Layer
│   ├── db.py                  # SQLite connection lifecycle, schema initialization, parameterized queries
│   └── securelink.db          # SQLite database (auto-generated)
│
├── services/                  # Business & Security Services
│   ├── encryption_service.py  # Zero-plaintext upload validation & AES-GCM encryption pipeline
│   ├── transfer_service.py    # Receiver decryption, GCM verification, and attack simulation lab
│   └── key_management.py      # RSA-3072 PKI generation and password-protected key unlocking
│
├── routes/                    # Web Application Blueprints
│   ├── auth.py                # Registration, rate-limited login, secure logout, PKI profile
│   ├── transfer.py            # Send file, received inbox, audit history, decrypt workbench, raw enc download
│   └── dashboard.py           # Real-time metrics dashboard, active cryptographic suite, security guide
│
├── templates/                 # Jinja2 HTML Templates (Dark Cybersecurity Theme)
│   ├── base.html              # Master layout with cyber navigation, flash alerts, and badges
│   ├── index.html             # Landing portal with hybrid crypto interactive sequence
│   ├── login.html             # Rate-limited authentication interface
│   ├── register.html          # Registration with on-the-fly RSA-3072 key generation notice
│   ├── dashboard.html         # Operations dashboard with live SQLite statistics & audit log
│   ├── send.html              # Drag-and-drop file upload with recipient PKI selection
│   ├── received.html          # Incoming encrypted transmissions table
│   ├── history.html           # Filterable transfer audit trail (All / Outbound / Inbound)
│   ├── decrypt.html           # Decryption workbench, side-by-side SHA-256 match & attack simulation lab
│   ├── security.html          # Security architecture, mathematical formulas, threat matrix & viva Q&A
│   └── profile.html           # Public key PEM display, SHA-256 fingerprint, and key protection guide
│
├── static/                    # Frontend Assets
│   ├── css/style.css          # Cyberpunk dark navy theme, neon borders, cards, and tables
│   └── js/main.js             # Clipboard copy helpers, drag-and-drop preview, auto-dismiss alerts
│
├── storage/
│   └── encrypted/             # Zero-plaintext storage directory for raw .enc ciphertext payloads
│
├── sample_files/              # Pre-generated realistic demonstration payloads (PDF, TXT, PNG, CSV)
│
├── screenshots/               # Actual application screenshots captured from running Flask server
│
├── docs/                      # Final Academic Deliverables
│   ├── SecureLink_Project_Report.pdf   # 21-page academic project report (ReportLab)
│   ├── SecureLink_Presentation.pptx   # 14-slide dark cybersecurity PowerPoint presentation (python-pptx)
│   ├── diagrams/              # Generated high-resolution architecture & ER diagrams
│   └── screenshots/           # Application screenshots for documentation embedding
│
├── scripts/                   # Automation & Generation Scripts
│   ├── capture_real_screenshots.py # Captures real screenshots from live Flask app via headless Chrome
│   ├── generate_diagrams.py   # Generates architecture, ERD, and GCM internal diagrams (matplotlib)
│   ├── generate_presentation.py# Compiles 14-slide PowerPoint presentation (python-pptx)
│   ├── generate_report.py     # Compiles 21-page academic report with numbered canvas (ReportLab)
│   └── generate_sample_files.py# Creates realistic sample files (PDF, TXT, PNG, CSV)
│
└── tests/                     # Automated Pytest Suite (25 Tests)
    ├── conftest.py            # Isolated test environment fixtures and temporary DB/storage
    ├── test_aes.py            # AES-256-GCM unit tests, nonces, wrong keys, and tag tampering
    ├── test_rsa.py            # RSA-3072 unit tests, OAEP key wrapping, wrong key rejection
    ├── test_hashing.py        # SHA-256 digest tests against NIST test vectors, constant-time checks
    ├── test_transfer.py       # End-to-end transfers with PDF, TXT, PNG, DOCX, 1MB files, and tamper test
    └── test_security.py       # Unauthorized user access, wrong password, rate-limiting, and validation
```

---

## 5. Installation & Setup (Windows PowerShell)

### Prerequisites
- Python 3.10 to Python 3.14 installed.
- PowerShell or Command Prompt.

### Step 1: Clone or Open Project Directory
```powershell
cd "d:\AntiGravity\College\DNS\Secure Link"
```

### Step 2: Create and Activate Virtual Environment (Optional but Recommended)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Required Dependencies
```powershell
python -m pip install -r requirements.txt
```

### Step 4: Initialize the SQLite Database
The database initializes automatically when the application starts. To initialize it explicitly:
```powershell
python -c "from database.db import init_db; init_db(); print('Database ready!')"
```

---

## 6. Running Automated Tests

SecureLink includes a comprehensive suite of **25 automated unit and end-to-end integration tests**:
```powershell
python -m pytest -v
```

### Test Coverage Highlights:
- **AES-GCM Suite:** 256-bit key generation, 96-bit nonce randomness, authenticated encryption/decryption, wrong key rejection, 1-bit ciphertext flip detection, authentication tag alteration detection, associated data mismatch rejection.
- **RSA-OAEP Suite:** RSA-3072 key pair generation, PKCS#8 password encryption, PEM serialization, OAEP session key encapsulation, wrong private key rejection.
- **SHA-256 Suite:** NIST test vector verification, chunked file hashing, constant-time `hmac.compare_digest` verification, salted password hashing.
- **End-to-End Suite:** Complete file transfers with `.txt`, `.pdf`, `.png`, `.docx`, and larger 1MB archives.
- **Security & Defensive Suite:** Unauthorized user decryption rejection, incorrect password rejection, rate-limiting lockout after repeated failures, file extension sanitization, empty file upload rejection.

---

## 7. Running the Application

Start the Flask application server:
```powershell
python app.py
```
*Console output:*
```
[*] Starting SecureLink Server on http://0.0.0.0:5000
[*] Access locally at: http://127.0.0.1:5000
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 8. Step-by-Step Demonstration Procedure (College Viva)

To present this project to examiners or professors, follow this sequential walkthrough:

### Scenario: Secure File Transfer between Alice and Bob
1. **Register User A (Sender):**
   - Click **Register** on the navbar.
   - Enter Username: `alice`, Email: `alice@university.edu`, Master Password: `AlicePassword2026!`.
   - Submit. Note the message: *An RSA-3072 key pair is generated; private key is encrypted with PKCS#8.*
2. **Register User B (Receiver) in an Incognito / Second Browser Window:**
   - Navigate to `http://127.0.0.1:5000/register`.
   - Enter Username: `bob`, Email: `bob@university.edu`, Master Password: `BobPassword2026!`.
   - Submit and Log in as `bob`.
3. **Send an Encrypted File (as Alice):**
   - In Alice's browser, navigate to **Send File**.
   - Select Recipient: `bob (bob@university.edu)`.
   - Select a sample file from `sample_files/` (e.g. `confidential_project_report.pdf` or `network_security_notes.txt`).
   - Click **Encrypt & Dispatch File**.
4. **Demonstrate Zero-Plaintext Storage:**
   - Open PowerShell and inspect the storage folder:
     ```powershell
     dir storage\encrypted
     ```
   - Notice the `.enc` filename (e.g. `9f8b..._confidential_project_report.pdf.enc`).
   - View the raw file content in Notepad or Hex viewer:
     ```powershell
     Get-Content -Path (Get-ChildItem storage\encrypted\*.enc)[0].FullName -TotalCount 5
     ```
   - *Proof:* The server stores only raw ciphertext bytes. There is zero plaintext on disk.
5. **Receive and Decrypt (as Bob):**
   - Switch to Bob's browser window. Click **Received Files**.
   - Notice the incoming transmission with status `READY TO DECRYPT` and the pre-encryption SHA-256 digest.
   - Click **Decrypt & Inspect**.
   - Enter Bob's master password (`BobPassword2026!`) to unlock Bob's private key.
   - Click **Decrypt & Verify File**.
6. **Observe the Cryptographic Verification Results:**
   - **Original Plaintext SHA-256 Digest:** Displayed in cyan.
   - **Decrypted Plaintext SHA-256 Digest:** Displayed in green.
   - **SHA-256 HASH MATCH:** `YES` (Bit-for-bit match confirmed).
   - **AES-GCM GHASH TAG:** `VALID` (Zero tampering detected).
   - Click **Download Decrypted Plaintext File** to download and verify the recovered PDF opens flawlessly.
7. **Demonstrate Active Tampering Attack Defense (High Viva Value!):**
   - On the same Decryption Workbench page, locate the red section: **Academic Attack Simulation Lab**.
   - Click **Simulate Ciphertext Tampering Attack** and confirm.
   - *What happens:* The server flips bytes in `storage/encrypted/*.enc` to simulate an active attacker modifying the payload in transit or disk.
   - Now attempt to decrypt the file again by providing Bob's password.
   - *Result:* **SECURITY ALERT: AES-256-GCM Authentication Tag mismatch!**
   - The GHASH tag check fails immediately with an `InvalidTag` exception. Decryption aborts instantly, proving that compromised payloads can never be released.

---

## 9. Multi-Device Network Demonstration (Same Wi-Fi)

To demonstrate file transfer between two distinct physical devices (e.g., laptop and smartphone, or two student laptops connected to the same college Wi-Fi):

1. **Find your machine's Local IPv4 Address:**
   ```powershell
   ipconfig
   ```
   Look for the `IPv4 Address` under your active Wi-Fi adapter (e.g. `192.168.1.45`).
2. **Launch the Server bound to `0.0.0.0`:**
   ```powershell
   python app.py
   ```
   (The server is already pre-configured to bind to `0.0.0.0:5000`).
3. **Ensure Windows Defender Firewall allows Python on Private Networks:**
   - If prompted, click *Allow access on private networks*.
4. **Access from Device 2 (Smartphone / Peer Laptop):**
   - Open a browser on Device 2 and enter:
     ```
     http://192.168.1.45:5000
     ```
   - Register Device 2 as User B.
   - Device 1 (Alice) sends a file to Device 2 (Bob).
   - Bob receives, decrypts, and downloads the file on their phone/laptop!

### Local HTTPS / TLS Configuration Note
> [!IMPORTANT]
> Ordinary HTTP over Wi-Fi is vulnerable to network sniffing of session cookies. For true end-to-end transport encryption during local college presentations:
> - Generate a local self-signed certificate using OpenSSL:
>   ```powershell
>   openssl req -x509 -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365
>   ```
> - Run Flask with SSL context enabled in `app.py`:
>   ```python
>   app.run(host='0.0.0.0', port=5000, ssl_context=('cert.pem', 'key.pem'))
>   ```
> - Access via `https://192.168.1.45:5000` (accepting the self-signed certificate warning).

---

## 10. Security Considerations & Defense Matrix

| Threat Vector | Attack Scenario | SecureLink Countermeasure |
| :--- | :--- | :--- |
| **Passive Sniffing** | Attacker captures packets on Wi-Fi | AES-256-GCM encryption + TLS transport |
| **Key Theft on Wire** | Attacker intercepts symmetric key | RSA-3072 OAEP key encapsulation; key only decryptable by receiver |
| **Payload Tampering** | Attacker modifies bits in transit or disk | AES-GCM GHASH authentication tag check fails; decryption aborted |
| **Server Disk Leak** | Rogue administrator dumps storage folder | Zero-Plaintext storage; only `.enc` ciphertext and wrapped keys exist |
| **Unauthorized Decryption** | User C attempts to decrypt Bob's file | Role-based check blocks non-recipients; User C lacks Bob's private RSA key |
| **Brute-Force Passwords** | Dictionary attack against login route | Automatic IP/username rate-limiting (lockout after 5 failed attempts) |
| **Malicious File Upload** | Attacker uploads `.exe` or shell script | Extension whitelist validation; filename sanitization via UUID |

---

## 11. Known Limitations & Academic Scope Disclaimer

- **Academic Context:** SecureLink is designed for educational demonstration and academic evaluation in the course **Data Network Security**. It has not undergone an independent commercial security audit.
- **In-Memory Key Ephemerality:** Private keys are decrypted in server RAM during the active decryption turn before being discarded. In high-assurance production environments, private keys should reside inside Hardware Security Modules (HSMs) or be processed client-side via the WebCrypto API.
- **Post-Quantum Consideration:** RSA-3072 is classical-secure (NIST compliant through 2030), but is theoretically susceptible to Shor's algorithm on large-scale quantum computers. Future migration would transition RSA-OAEP to NIST FIPS 203 ML-KEM (Kyber).

---

## 12. Final Deliverables Summary

- **Working Source Code:** Flask 3.x, SQLite, Python Cryptography (AES-GCM, RSA-3072, OAEP, SHA-256).
- **Automated Test Suite:** 25 passing pytest unit and integration tests (`tests/`).
- **Academic Project Report:** `docs/SecureLink_Project_Report.pdf` (21 pages, formal academic format, ReportLab).
- **Presentation Slides:** `docs/SecureLink_Presentation.pptx` (14 slides, dark cybersecurity theme, python-pptx).
- **Real Application Screenshots:** 12 genuine screenshots captured from the live application (`screenshots/`).
- **Architecture Diagrams:** High-resolution diagrams for Hybrid Cryptography, Database Schema, and AES-GCM internals (`docs/diagrams/`).
- **Sample Test Files:** Ready-to-use demonstration files (`sample_files/`).

