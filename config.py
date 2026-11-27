import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Application configuration for SecureLink."""
    SECRET_KEY = os.environ.get("SECURELINK_SECRET_KEY", "securelink-hybrid-crypto-dns-college-2026-secret-key-3072-gcm")
    
    # Database
    DATABASE_PATH = os.path.join(BASE_DIR, "database", "securelink.db")
    
    # Storage
    STORAGE_DIR = os.path.join(BASE_DIR, "storage", "encrypted")
    
    # Upload constraints
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit
    ALLOWED_EXTENSIONS = {
        'txt', 'pdf', 'png', 'jpg', 'jpeg', 'docx', 
        'xlsx', 'zip', 'csv', 'json', 'py', 'md'
    }
    
    # Cryptographic standards
    RSA_KEY_SIZE = 3072  # RSA-3072 for long-term security
    RSA_PUBLIC_EXPONENT = 65537
    AES_KEY_SIZE_BYTES = 32  # AES-256 (256 bits)
    AES_NONCE_SIZE_BYTES = 12  # 96 bits standard for GCM
    
    # Rate Limiting
    MAX_FAILED_LOGIN_ATTEMPTS = 5
    LOGIN_LOCKOUT_MINUTES = 10
    
    # Session Cookie Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

