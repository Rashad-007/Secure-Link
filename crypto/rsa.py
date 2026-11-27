from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend

def generate_rsa_keypair(key_size: int = 3072):
    """
    Generate an RSA key pair with specified key size (default RSA-3072).
    Returns (private_key, public_key) objects.
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key

def serialize_private_key(private_key, password: str) -> str:
    """
    Serialize private key to PEM format encrypted with user password using PKCS#8
    and BestAvailableEncryption (AES-256-CBC with PBKDF2/scrypt).
    """
    if not password:
        raise ValueError("Password is required to encrypt the private key.")
        
    pem_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(password.encode('utf-8'))
    )
    return pem_bytes.decode('utf-8')

def deserialize_private_key(pem_str: str, password: str):
    """
    Deserialize private key from encrypted PEM string using user password.
    Raises ValueError if password is wrong or PEM is corrupt.
    """
    try:
        return serialization.load_pem_private_key(
            pem_str.encode('utf-8'),
            password=password.encode('utf-8') if password else None,
            backend=default_backend()
        )
    except Exception as exc:
        raise ValueError("Failed to unlock RSA private key. Incorrect password or invalid key format.") from exc

def serialize_public_key(public_key) -> str:
    """Serialize public key to standard PEM format."""
    pem_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem_bytes.decode('utf-8')

def deserialize_public_key(pem_str: str):
    """Deserialize public key from PEM string."""
    try:
        return serialization.load_pem_public_key(
            pem_str.encode('utf-8'),
            backend=default_backend()
        )
    except Exception as exc:
        raise ValueError("Invalid RSA public key PEM format.") from exc

def encrypt_aes_key_with_rsa(public_key, aes_key: bytes) -> bytes:
    """
    Encrypt a 256-bit AES symmetric key using RSA-OAEP with SHA-256.
    """
    return public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def decrypt_aes_key_with_rsa(private_key, encrypted_aes_key: bytes) -> bytes:
    """
    Decrypt an RSA-OAEP encrypted AES key using the receiver's RSA-3072 private key.
    """
    try:
        return private_key.decrypt(
            encrypted_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    except Exception as exc:
        raise ValueError("RSA-OAEP decryption failed. AES key could not be recovered with this private key.") from exc

