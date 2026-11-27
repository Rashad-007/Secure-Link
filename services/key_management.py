from crypto.rsa import (
    generate_rsa_keypair,
    serialize_private_key,
    deserialize_private_key,
    serialize_public_key,
    deserialize_public_key
)
from database.db import query_db, execute_db

def create_user_keys(password: str) -> tuple[str, str]:
    """
    Generate an RSA-3072 key pair for a newly registered user,
    encrypt the private key using the user's password via PKCS#8,
    and return (public_key_pem, encrypted_private_key_pem).
    """
    private_key, public_key = generate_rsa_keypair(key_size=3072)
    enc_private_pem = serialize_private_key(private_key, password)
    public_pem = serialize_public_key(public_key)
    return public_pem, enc_private_pem

def get_receiver_public_key(receiver_id: int):
    """Fetch and deserialize a receiver's RSA public key by user ID."""
    user = query_db("SELECT public_key FROM users WHERE user_id = ?", (receiver_id,), one=True)
    if not user:
        raise ValueError(f"Receiver with ID {receiver_id} does not exist.")
    return deserialize_public_key(user["public_key"])

def unlock_user_private_key(user_id: int, password: str):
    """
    Retrieve and decrypt the user's stored RSA-3072 private key
    using their supplied password.
    """
    user = query_db("SELECT encrypted_private_key FROM users WHERE user_id = ?", (user_id,), one=True)
    if not user:
        raise ValueError("User not found.")
    return deserialize_private_key(user["encrypted_private_key"], password)

