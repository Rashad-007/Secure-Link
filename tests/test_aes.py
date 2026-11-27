import pytest
from crypto.aes import generate_aes_key, generate_nonce, encrypt_aes_gcm, decrypt_aes_gcm

def test_aes_key_generation():
    key1 = generate_aes_key()
    key2 = generate_aes_key()
    assert len(key1) == 32
    assert len(key2) == 32
    assert key1 != key2

def test_aes_nonce_generation():
    n1 = generate_nonce()
    n2 = generate_nonce()
    assert len(n1) == 12
    assert len(n2) == 12
    assert n1 != n2

def test_aes_gcm_encrypt_decrypt():
    key = generate_aes_key()
    plaintext = b"Sensitive College Data Network Security Packet Payload"
    associated_data = b"metadata_header"

    ciphertext, nonce, tag = encrypt_aes_gcm(key, plaintext, associated_data=associated_data)

    assert len(ciphertext) == len(plaintext)
    assert len(nonce) == 12
    assert len(tag) == 16
    assert ciphertext != plaintext

    recovered = decrypt_aes_gcm(key, nonce, ciphertext, tag, associated_data=associated_data)
    assert recovered == plaintext

def test_aes_gcm_wrong_key_fails():
    key1 = generate_aes_key()
    key2 = generate_aes_key()
    plaintext = b"Confidential DNS exam records"

    ciphertext, nonce, tag = encrypt_aes_gcm(key1, plaintext)

    with pytest.raises(ValueError, match="AES-GCM Integrity Check Failed"):
        decrypt_aes_gcm(key2, nonce, ciphertext, tag)

def test_aes_gcm_modified_ciphertext_fails():
    key = generate_aes_key()
    plaintext = b"Critical financial transfer record"

    ciphertext, nonce, tag = encrypt_aes_gcm(key, plaintext)

    # Tamper with 1 byte in ciphertext
    tampered_ciphertext = bytearray(ciphertext)
    tampered_ciphertext[0] ^= 0xFF

    with pytest.raises(ValueError, match="AES-GCM Integrity Check Failed"):
        decrypt_aes_gcm(key, nonce, bytes(tampered_ciphertext), tag)

def test_aes_gcm_modified_tag_fails():
    key = generate_aes_key()
    plaintext = b"Authentication tag integrity verification test"

    ciphertext, nonce, tag = encrypt_aes_gcm(key, plaintext)

    # Tamper with authentication tag
    tampered_tag = bytearray(tag)
    tampered_tag[0] ^= 0x01

    with pytest.raises(ValueError, match="AES-GCM Integrity Check Failed"):
        decrypt_aes_gcm(key, nonce, ciphertext, bytes(tampered_tag))

def test_aes_gcm_associated_data_mismatch():
    key = generate_aes_key()
    plaintext = b"Binds filename to ciphertext"
    original_ad = b"file_report.pdf"
    tampered_ad = b"hacked_report.pdf"

    ciphertext, nonce, tag = encrypt_aes_gcm(key, plaintext, associated_data=original_ad)

    with pytest.raises(ValueError, match="AES-GCM Integrity Check Failed"):
        decrypt_aes_gcm(key, nonce, ciphertext, tag, associated_data=tampered_ad)

