import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

TAG_LENGTH_BYTES = 16  # 128-bit authentication tag standard for AES-GCM

def generate_aes_key() -> bytes:
    """Generate a cryptographically secure 256-bit (32 bytes) AES key."""
    return AESGCM.generate_key(bit_length=256)

def generate_nonce() -> bytes:
    """Generate a 96-bit (12 bytes) cryptographically secure nonce for AES-GCM."""
    return os.urandom(12)

def encrypt_aes_gcm(key: bytes, plaintext: bytes, associated_data: bytes = None) -> tuple[bytes, bytes, bytes]:
    """
    Encrypt plaintext using AES-256-GCM.
    
    Returns:
        tuple (ciphertext_without_tag: bytes, nonce: bytes, tag: bytes)
    """
    if len(key) != 32:
        raise ValueError("AES key must be exactly 32 bytes (256 bits).")
        
    nonce = generate_nonce()
    aesgcm = AESGCM(key)
    # aesgcm.encrypt returns ciphertext with 16-byte authentication tag appended
    encrypted_payload = aesgcm.encrypt(nonce, plaintext, associated_data)
    
    ciphertext = encrypted_payload[:-TAG_LENGTH_BYTES]
    tag = encrypted_payload[-TAG_LENGTH_BYTES:]
    
    return ciphertext, nonce, tag

def decrypt_aes_gcm(key: bytes, nonce: bytes, ciphertext: bytes, tag: bytes, associated_data: bytes = None) -> bytes:
    """
    Decrypt ciphertext using AES-256-GCM and verify the authentication tag.
    
    Raises:
        ValueError if the authentication tag check fails (tampered file or wrong key).
    """
    if len(key) != 32:
        raise ValueError("AES key must be exactly 32 bytes (256 bits).")
    if len(nonce) != 12:
        raise ValueError("Nonce must be exactly 12 bytes (96 bits).")
    if len(tag) != TAG_LENGTH_BYTES:
        raise ValueError("Authentication tag must be exactly 16 bytes (128 bits).")

    aesgcm = AESGCM(key)
    full_payload = ciphertext + tag
    
    try:
        decrypted_data = aesgcm.decrypt(nonce, full_payload, associated_data)
        return decrypted_data
    except InvalidTag as exc:
        raise ValueError("AES-GCM Integrity Check Failed: Authentication tag mismatch. File data has been altered or key is invalid.") from exc

