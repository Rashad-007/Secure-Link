import hashlib
import hmac
from werkzeug.security import generate_password_hash, check_password_hash

def compute_sha256_bytes(data: bytes) -> str:
    """Compute the SHA-256 hexadecimal hash string for binary data."""
    hasher = hashlib.sha256()
    hasher.update(data)
    return hasher.hexdigest()

def compute_sha256_file(file_path: str) -> str:
    """Compute the SHA-256 hexadecimal hash string of a file in chunks."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def verify_sha256(expected_hash: str, actual_hash: str) -> bool:
    """
    Perform a secure constant-time comparison of two SHA-256 hashes
    to mitigate timing attacks.
    """
    if not expected_hash or not actual_hash:
        return False
    return hmac.compare_digest(expected_hash.lower(), actual_hash.lower())

def hash_user_password(password: str) -> str:
    """Hash password using Werkzeug's secure hashing (scrypt or pbkdf2:sha256)."""
    return generate_password_hash(password)

def verify_user_password(password_hash: str, password: str) -> bool:
    """Verify user password against stored hash."""
    return check_password_hash(password_hash, password)

