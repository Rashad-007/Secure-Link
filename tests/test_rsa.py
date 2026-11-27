import pytest
from crypto.rsa import (
    generate_rsa_keypair,
    serialize_private_key,
    deserialize_private_key,
    serialize_public_key,
    deserialize_public_key,
    encrypt_aes_key_with_rsa,
    decrypt_aes_key_with_rsa
)
from crypto.aes import generate_aes_key

def test_rsa_keypair_generation():
    priv, pub = generate_rsa_keypair(key_size=3072)
    assert priv.key_size == 3072
    assert pub.key_size == 3072

def test_rsa_key_serialization_with_password():
    priv, pub = generate_rsa_keypair(key_size=3072)
    password = "CorrectSuperSecurePassword123!"

    enc_pem = serialize_private_key(priv, password)
    assert "-----BEGIN ENCRYPTED PRIVATE KEY-----" in enc_pem

    # Reload with correct password
    loaded_priv = deserialize_private_key(enc_pem, password)
    assert loaded_priv.key_size == 3072

    # Attempt reload with wrong password
    with pytest.raises(ValueError, match="Failed to unlock RSA private key"):
        deserialize_private_key(enc_pem, "WrongPassword!")

def test_rsa_public_key_serialization():
    priv, pub = generate_rsa_keypair(key_size=3072)
    pub_pem = serialize_public_key(pub)
    assert "-----BEGIN PUBLIC KEY-----" in pub_pem

    loaded_pub = deserialize_public_key(pub_pem)
    assert loaded_pub.key_size == 3072

def test_rsa_oaep_encrypt_decrypt_aes_key():
    priv, pub = generate_rsa_keypair(key_size=3072)
    aes_session_key = generate_aes_key()

    # Encrypt 256-bit AES key with RSA-OAEP
    encrypted_key = encrypt_aes_key_with_rsa(pub, aes_session_key)
    assert len(encrypted_key) == 384  # 3072 bits / 8 = 384 bytes
    assert encrypted_key != aes_session_key

    # Decrypt with private key
    decrypted_key = decrypt_aes_key_with_rsa(priv, encrypted_key)
    assert decrypted_key == aes_session_key

def test_rsa_oaep_wrong_private_key_fails():
    priv1, pub1 = generate_rsa_keypair(key_size=3072)
    priv2, pub2 = generate_rsa_keypair(key_size=3072)
    aes_session_key = generate_aes_key()

    # Encrypt with pub1
    encrypted_key = encrypt_aes_key_with_rsa(pub1, aes_session_key)

    # Attempt decrypt with priv2
    with pytest.raises(ValueError, match="RSA-OAEP decryption failed"):
        decrypt_aes_key_with_rsa(priv2, encrypted_key)

