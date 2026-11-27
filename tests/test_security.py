import io
import pytest
from database.db import query_db, execute_db
from services.key_management import create_user_keys
from services.encryption_service import process_and_encrypt_upload
from services.transfer_service import decrypt_and_verify_transfer
from werkzeug.datastructures import FileStorage

def create_user(username, password):
    pub, priv = create_user_keys(password)
    from crypto.hashing import hash_user_password
    user_id = execute_db(
        "INSERT INTO users (username, email, password_hash, public_key, encrypted_private_key) VALUES (?, ?, ?, ?, ?)",
        (username, f"{username}@test.edu", hash_user_password(password), pub, priv)
    )
    return user_id

def test_unauthorized_user_cannot_decrypt(app_instance):
    with app_instance.app_context():
        user_a = create_user("user_a", "PassA12345!")
        user_b = create_user("user_b", "PassB12345!")
        user_c = create_user("user_c", "PassC12345!")  # Unauthorized eavesdropper

        content = b"Top secret communication intended only for User B"
        storage = FileStorage(stream=io.BytesIO(content), filename="classified.txt")
        res = process_and_encrypt_upload(storage, user_a, user_b)

        # User C tries to decrypt User B's file
        with pytest.raises(PermissionError, match="Unauthorized: Only the intended receiver"):
            decrypt_and_verify_transfer(res['transfer_id'], user_c, "PassC12345!")

def test_incorrect_password_fails_private_key_unlock(app_instance):
    with app_instance.app_context():
        user_a = create_user("user_x", "PassX12345!")
        user_b = create_user("user_y", "PassY12345!")

        content = b"Some data packet"
        storage = FileStorage(stream=io.BytesIO(content), filename="packet.txt")
        res = process_and_encrypt_upload(storage, user_a, user_b)

        # User B gives wrong password
        with pytest.raises(ValueError, match="Invalid password: Failed to unlock RSA-3072 private key"):
            decrypt_and_verify_transfer(res['transfer_id'], user_b, "WrongPasswordHere!")

def test_auth_failure_and_rate_limiting(client, app_instance):
    with app_instance.app_context():
        create_user("target_user", "ValidPassword123!")

    # Attempt 3 failed logins (MAX_FAILED_LOGIN_ATTEMPTS in TestConfig is 3)
    for _ in range(3):
        res = client.post('/login', data={"username": "target_user", "password": "WrongPassword"})
        assert b"Invalid credentials" in res.data

    # 4th attempt should hit rate limit lockout
    res_lockout = client.post('/login', data={"username": "target_user", "password": "ValidPassword123!"})
    assert b"Account locked temporarily" in res_lockout.data

def test_disallowed_file_extension(app_instance):
    with app_instance.app_context():
        user_a = create_user("sender_disallowed", "PassA12345!")
        user_b = create_user("receiver_disallowed", "PassB12345!")

        bad_file = FileStorage(stream=io.BytesIO(b"malicious executable"), filename="trojan.exe")
        with pytest.raises(ValueError, match="File type not permitted"):
            process_and_encrypt_upload(bad_file, user_a, user_b)

def test_empty_file_upload_rejected(app_instance):
    with app_instance.app_context():
        user_a = create_user("sender_empty", "PassA12345!")
        user_b = create_user("receiver_empty", "PassB12345!")

        empty_file = FileStorage(stream=io.BytesIO(b""), filename="empty.txt")
        with pytest.raises(ValueError, match="Uploaded file is empty"):
            process_and_encrypt_upload(empty_file, user_a, user_b)

