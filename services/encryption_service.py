import os
import uuid
from flask import current_app, has_app_context
from werkzeug.utils import secure_filename
from config import Config
from crypto.aes import generate_aes_key, encrypt_aes_gcm
from crypto.rsa import encrypt_aes_key_with_rsa
from crypto.hashing import compute_sha256_bytes
from database.db import execute_db
from services.key_management import get_receiver_public_key

def get_storage_dir():
    return current_app.config.get('STORAGE_DIR', Config.STORAGE_DIR) if has_app_context() else Config.STORAGE_DIR

def is_allowed_file(filename: str) -> bool:
    """Check if file has an allowed extension."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', Config.ALLOWED_EXTENSIONS) if has_app_context() else Config.ALLOWED_EXTENSIONS
    return ext in allowed

def process_and_encrypt_upload(file_storage, sender_id: int, receiver_id: int, client_ip: str = None) -> dict:
    """
    Core encryption pipeline for file uploads:
    1. Read and validate file content.
    2. Compute SHA-256 digest of original plaintext.
    3. Generate a 256-bit AES key and a 96-bit nonce.
    4. Encrypt file using AES-256-GCM (producing ciphertext and 128-bit tag).
    5. Save encrypted ciphertext into server-side encrypted storage.
    6. Encrypt AES key using Receiver's RSA-3072 public key with RSA-OAEP (SHA-256).
    7. Save transfer metadata into SQLite.
    8. Discard plaintext and raw AES key from memory.
    """
    raw_filename = file_storage.filename
    clean_filename = secure_filename(raw_filename)
    if not clean_filename:
        clean_filename = f"file_{uuid.uuid4().hex[:8]}"

    if not is_allowed_file(clean_filename):
        raise ValueError("File type not permitted. Allowed: " + ", ".join(Config.ALLOWED_EXTENSIONS))

    file_bytes = file_storage.read()
    file_size = len(file_bytes)

    if file_size == 0:
        raise ValueError("Uploaded file is empty.")
    if file_size > Config.MAX_CONTENT_LENGTH:
        raise ValueError(f"File size exceeds maximum allowed limit of {Config.MAX_CONTENT_LENGTH // (1024*1024)}MB.")

    # 1. Compute SHA-256 of original plaintext
    original_sha256 = compute_sha256_bytes(file_bytes)

    # 2. Generate cryptographically random 256-bit AES key
    aes_key = generate_aes_key()

    # 3. Encrypt file bytes with AES-256-GCM
    # Associated data binds original filename to the cryptographic tag
    associated_data = clean_filename.encode('utf-8')
    ciphertext, nonce, auth_tag = encrypt_aes_gcm(aes_key, file_bytes, associated_data=associated_data)

    # 4. Save ciphertext to encrypted storage
    storage_dir = get_storage_dir()
    os.makedirs(storage_dir, exist_ok=True)
    encrypted_filename = f"{uuid.uuid4().hex}_{clean_filename}.enc"
    encrypted_file_path = os.path.join(storage_dir, encrypted_filename)
    with open(encrypted_file_path, "wb") as f:
        f.write(ciphertext)

    # 5. Encrypt AES key using Receiver's RSA-3072 public key
    receiver_pub_key = get_receiver_public_key(receiver_id)
    encrypted_aes_key = encrypt_aes_key_with_rsa(receiver_pub_key, aes_key)

    # 6. Erase AES key from memory
    del aes_key
    del file_bytes

    # 7. Record transfer in database
    transfer_id = execute_db(
        '''
        INSERT INTO transfers (
            sender_id, receiver_id, original_filename, encrypted_filename,
            file_size, encrypted_aes_key, nonce, auth_tag, original_sha256,
            transfer_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'SENT')
        ''',
        (
            sender_id, receiver_id, clean_filename, encrypted_filename,
            file_size, encrypted_aes_key, nonce, auth_tag, original_sha256
        )
    )

    # 8. Record audit log
    execute_db(
        '''
        INSERT INTO audit_logs (user_id, action, details, ip_address)
        VALUES (?, 'FILE_SENT', ?, ?)
        ''',
        (sender_id, f"File '{clean_filename}' ({file_size} bytes) encrypted and sent to user ID {receiver_id}", client_ip)
    )

    return {
        "transfer_id": transfer_id,
        "original_filename": clean_filename,
        "file_size": file_size,
        "original_sha256": original_sha256,
        "encrypted_filename": encrypted_filename
    }
