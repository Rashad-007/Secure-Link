import os
import tempfile
from crypto.hashing import (
    compute_sha256_bytes,
    compute_sha256_file,
    verify_sha256,
    hash_user_password,
    verify_user_password
)

def test_sha256_bytes():
    # Test vector: empty string
    empty_digest = compute_sha256_bytes(b"")
    assert empty_digest == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    # Known NIST test vector
    sample_digest = compute_sha256_bytes(b"abc")
    assert sample_digest == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"

def test_sha256_file():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"Data Network Security College Mini-Project")
        f.flush()
        file_path = f.name

    try:
        digest = compute_sha256_file(file_path)
        expected = compute_sha256_bytes(b"Data Network Security College Mini-Project")
        assert digest == expected
    finally:
        os.remove(file_path)

def test_sha256_verification():
    h1 = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    h2 = "BA7816BF8F01CFEA414140DE5DAE2223B00361A396177A9CB410FF61F20015AD"
    h3 = "0000000000000000000000000000000000000000000000000000000000000000"

    assert verify_sha256(h1, h2) is True
    assert verify_sha256(h1, h3) is False
    assert verify_sha256(h1, "") is False

def test_password_hashing():
    pwd = "MySecretCollegePassword2026!"
    hashed = hash_user_password(pwd)

    # Different salts ensure different hashes
    hashed2 = hash_user_password(pwd)
    assert hashed != hashed2

    assert verify_user_password(hashed, pwd) is True
    assert verify_user_password(hashed, "WrongPassword") is False

