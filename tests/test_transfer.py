import io
import pytest
from database.db import query_db
from services.key_management import create_user_keys
from services.encryption_service import process_and_encrypt_upload
from services.transfer_service import decrypt_and_verify_transfer, simulate_tampering_attack
from werkzeug.datastructures import FileStorage

def create_test_user(app_instance, username, password):
    with app_instance.app_context():
        pub, priv = create_user_keys(password)
        from crypto.hashing import hash_user_password
        from database.db import execute_db
        user_id = execute_db(
            "INSERT INTO users (username, email, password_hash, public_key, encrypted_private_key) VALUES (?, ?, ?, ?, ?)",
            (username, f"{username}@test.edu", hash_user_password(password), pub, priv)
        )
        return user_id

def test_end_to_end_txt_transfer(app_instance):
    with app_instance.app_context():
        sender_id = create_test_user(app_instance, "alice", "AlicePass123!")
        receiver_id = create_test_user(app_instance, "bob", "BobPass123!")

        content = b"Data Network Security - College Mini-Project Confidential Transmit."
        file_storage = FileStorage(stream=io.BytesIO(content), filename="notes.txt")

        # 1. Process upload and encrypt
        result = process_and_encrypt_upload(file_storage, sender_id, receiver_id)
        assert result['original_filename'] == "notes.txt"
        assert result['file_size'] == len(content)

        # 2. Decrypt as receiver
        dec_result = decrypt_and_verify_transfer(result['transfer_id'], receiver_id, "BobPass123!")
        assert dec_result['plaintext'] == content
        assert dec_result['integrity_verified'] is True
        assert dec_result['original_sha256'] == dec_result['decrypted_sha256']

def test_transfer_pdf_and_images(app_instance):
    with app_instance.app_context():
        sender_id = create_test_user(app_instance, "charlie", "CharliePass123!")
        receiver_id = create_test_user(app_instance, "david", "DavidPass123!")

        # Mock PDF Header bytes
        pdf_bytes = b"%PDF-1.4\n1 0 obj\n<< /Title (Network Security) >>\nendobj\n%%EOF"
        pdf_storage = FileStorage(stream=io.BytesIO(pdf_bytes), filename="report.pdf")
        res_pdf = process_and_encrypt_upload(pdf_storage, sender_id, receiver_id)

        dec_pdf = decrypt_and_verify_transfer(res_pdf['transfer_id'], receiver_id, "DavidPass123!")
        assert dec_pdf['plaintext'] == pdf_bytes
        assert dec_pdf['integrity_verified'] is True

        # Mock PNG Header bytes
        png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + (b"\xAA" * 200)
        png_storage = FileStorage(stream=io.BytesIO(png_bytes), filename="diagram.png")
        res_png = process_and_encrypt_upload(png_storage, sender_id, receiver_id)

        dec_png = decrypt_and_verify_transfer(res_png['transfer_id'], receiver_id, "DavidPass123!")
        assert dec_png['plaintext'] == png_bytes
        assert dec_png['integrity_verified'] is True

def test_transfer_docx_and_larger_file(app_instance):
    with app_instance.app_context():
        sender_id = create_test_user(app_instance, "eve", "EvePass123!")
        receiver_id = create_test_user(app_instance, "frank", "FrankPass123!")

        # Mock DOCX (ZIP signature)
        docx_bytes = b"PK\x03\x04" + (b"Document XML payload" * 50)
        docx_storage = FileStorage(stream=io.BytesIO(docx_bytes), filename="project.docx")
        res_docx = process_and_encrypt_upload(docx_storage, sender_id, receiver_id)

        dec_docx = decrypt_and_verify_transfer(res_docx['transfer_id'], receiver_id, "FrankPass123!")
        assert dec_docx['plaintext'] == docx_bytes
        assert dec_docx['integrity_verified'] is True

        # 1MB file test
        large_bytes = b"SecureLinkBulkPayloadData2026" * 35000  # ~1MB
        large_storage = FileStorage(stream=io.BytesIO(large_bytes), filename="archive.zip")
        res_large = process_and_encrypt_upload(large_storage, sender_id, receiver_id)

        dec_large = decrypt_and_verify_transfer(res_large['transfer_id'], receiver_id, "FrankPass123!")
        assert dec_large['plaintext'] == large_bytes
        assert dec_large['integrity_verified'] is True

def test_detection_of_modified_encrypted_data(app_instance):
    with app_instance.app_context():
        sender_id = create_test_user(app_instance, "grace", "GracePass123!")
        receiver_id = create_test_user(app_instance, "heidi", "HeidiPass123!")

        content = b"Original uncorrupted financial record"
        file_storage = FileStorage(stream=io.BytesIO(content), filename="ledger.csv")
        res = process_and_encrypt_upload(file_storage, sender_id, receiver_id)

        # Simulate tampering on the server disk
        simulate_tampering_attack(res['transfer_id'], sender_id)

        # Attempt to decrypt - must fail with AES-GCM Authentication error!
        with pytest.raises(ValueError, match="AES-256-GCM Authentication Tag mismatch"):
            decrypt_and_verify_transfer(res['transfer_id'], receiver_id, "HeidiPass123!")

        # Verify transfer status in DB is marked as TAMPERED
        t = query_db("SELECT transfer_status, is_tampered FROM transfers WHERE transfer_id = ?", (res['transfer_id'],), one=True)
        assert t['transfer_status'] == 'TAMPERED'
        assert t['is_tampered'] == 1

