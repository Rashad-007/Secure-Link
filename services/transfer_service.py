import os
from datetime import datetime
from flask import current_app, has_app_context
from config import Config
from crypto.aes import decrypt_aes_gcm
from crypto.rsa import decrypt_aes_key_with_rsa
from crypto.hashing import compute_sha256_bytes, verify_sha256
from database.db import query_db, execute_db
from services.key_management import unlock_user_private_key

def get_storage_dir():
    return current_app.config.get('STORAGE_DIR', Config.STORAGE_DIR) if has_app_context() else Config.STORAGE_DIR

def get_transfer_by_id(transfer_id: int):
    """Retrieve transfer record with sender and receiver usernames."""
    query = '''
    SELECT t.*, 
           s.username AS sender_username, s.email AS sender_email,
           r.username AS receiver_username, r.email AS receiver_email
    FROM transfers t
    JOIN users s ON t.sender_id = s.user_id
    JOIN users r ON t.receiver_id = r.user_id
    WHERE t.transfer_id = ?
    '''
    return query_db(query, (transfer_id,), one=True)

def check_transfer_authorization(transfer, user_id: int):
    """Verify that user is either sender or receiver of the transfer."""
    if not transfer:
        raise ValueError("Transfer record not found.")
    if transfer['sender_id'] != user_id and transfer['receiver_id'] != user_id:
        raise PermissionError("Access Denied: You are not authorized to view or access this transfer.")

def decrypt_and_verify_transfer(transfer_id: int, user_id: int, password: str, client_ip: str = None) -> dict:
    """
    Decryption and Verification Pipeline:
    1. Authorization Check (only intended receiver can decrypt).
    2. Unlock receiver's RSA-3072 private key with password.
    3. Recover 256-bit AES key via RSA-OAEP decryption.
    4. Decrypt file data using AES-256-GCM and verify authentication tag.
    5. Compute SHA-256 hash of recovered plaintext.
    6. Verify SHA-256 against stored original digest.
    7. Update database status and audit log.
    """
    transfer = get_transfer_by_id(transfer_id)
    if not transfer:
        raise ValueError("Transfer record not found.")
    
    if transfer['receiver_id'] != user_id:
        raise PermissionError("Unauthorized: Only the intended receiver can decrypt this file.")

    encrypted_file_path = os.path.join(get_storage_dir(), transfer['encrypted_filename'])
    if not os.path.exists(encrypted_file_path):
        raise FileNotFoundError("Encrypted file payload missing from storage.")

    with open(encrypted_file_path, "rb") as f:
        ciphertext = f.read()

    # 1. Unlock receiver's private key
    try:
        private_key = unlock_user_private_key(user_id, password)
    except Exception as exc:
        raise ValueError("Invalid password: Failed to unlock RSA-3072 private key.") from exc

    # 2. Decrypt AES key with RSA-OAEP
    try:
        aes_key = decrypt_aes_key_with_rsa(private_key, transfer['encrypted_aes_key'])
    except Exception as exc:
        raise ValueError("Cryptographic Failure: Unable to decrypt AES key with RSA private key.") from exc

    # 3. Decrypt ciphertext using AES-256-GCM
    associated_data = transfer['original_filename'].encode('utf-8')
    try:
        plaintext = decrypt_aes_gcm(
            aes_key,
            transfer['nonce'],
            ciphertext,
            transfer['auth_tag'],
            associated_data=associated_data
        )
    except ValueError as e:
        # AES-GCM tag verification failure
        execute_db(
            "UPDATE transfers SET transfer_status = 'TAMPERED', is_tampered = 1 WHERE transfer_id = ?",
            (transfer_id,)
        )
        execute_db(
            '''
            INSERT INTO audit_logs (user_id, action, details, ip_address)
            VALUES (?, 'TAMPER_ALERT', ?, ?)
            ''',
            (user_id, f"AES-GCM integrity check failed on transfer #{transfer_id} (Tampering detected!)", client_ip)
        )
        raise ValueError("SECURITY ALERT: AES-256-GCM Authentication Tag mismatch! The encrypted file payload was altered or corrupted in storage.") from e

    # 4. Compute SHA-256 hash of decrypted content
    decrypted_sha256 = compute_sha256_bytes(plaintext)

    # 5. Verify integrity against original digest
    integrity_verified = verify_sha256(transfer['original_sha256'], decrypted_sha256)

    status = 'VERIFIED' if integrity_verified else 'CORRUPT'
    execute_db(
        '''
        UPDATE transfers 
        SET transfer_status = ?, 
            decrypted_at = CURRENT_TIMESTAMP, 
            verified_sha256 = ?
        WHERE transfer_id = ?
        ''',
        (status, decrypted_sha256, transfer_id)
    )

    execute_db(
        '''
        INSERT INTO audit_logs (user_id, action, details, ip_address)
        VALUES (?, 'FILE_DECRYPTED', ?, ?)
        ''',
        (user_id, f"File '{transfer['original_filename']}' successfully decrypted. SHA-256 match: {integrity_verified}", client_ip)
    )

    return {
        "plaintext": plaintext,
        "filename": transfer['original_filename'],
        "original_sha256": transfer['original_sha256'],
        "decrypted_sha256": decrypted_sha256,
        "integrity_verified": integrity_verified
    }

def simulate_tampering_attack(transfer_id: int, user_id: int, client_ip: str = None) -> bool:
    """
    Academic / Demonstration feature:
    Intentionally flips bytes in the server-side encrypted file to simulate
    an active MITM / attacker payload modification in storage or transit.
    """
    transfer = get_transfer_by_id(transfer_id)
    check_transfer_authorization(transfer, user_id)

    encrypted_file_path = os.path.join(get_storage_dir(), transfer['encrypted_filename'])
    if not os.path.exists(encrypted_file_path):
        raise FileNotFoundError("Encrypted file payload missing from storage.")

    with open(encrypted_file_path, "rb") as f:
        data = bytearray(f.read())

    if len(data) == 0:
        raise ValueError("Cannot tamper with empty payload.")

    # Flip the first byte
    data[0] ^= 0xFF
    # Flip middle byte if size > 1
    if len(data) > 2:
        mid = len(data) // 2
        data[mid] ^= 0xAA

    with open(encrypted_file_path, "wb") as f:
        f.write(data)

    execute_db(
        "UPDATE transfers SET is_tampered = 1, transfer_status = 'TAMPERED' WHERE transfer_id = ?",
        (transfer_id,)
    )

    execute_db(
        '''
        INSERT INTO audit_logs (user_id, action, details, ip_address)
        VALUES (?, 'TAMPER_SIMULATED', ?, ?)
        ''',
        (user_id, f"Demonstration: Manually corrupted bytes in encrypted storage for transfer #{transfer_id}", client_ip)
    )

    return True

def get_dashboard_statistics(user_id: int) -> dict:
    """Derive live statistical values for user dashboard from database."""
    sent = query_db(
        "SELECT COUNT(*) as count, COALESCE(SUM(file_size), 0) as total_size FROM transfers WHERE sender_id = ?",
        (user_id,),
        one=True
    )
    received = query_db(
        "SELECT COUNT(*) as count, COALESCE(SUM(file_size), 0) as total_size FROM transfers WHERE receiver_id = ?",
        (user_id,),
        one=True
    )
    successful = query_db(
        "SELECT COUNT(*) as count FROM transfers WHERE (sender_id = ? OR receiver_id = ?) AND transfer_status = 'VERIFIED'",
        (user_id, user_id),
        one=True
    )
    tampered = query_db(
        "SELECT COUNT(*) as count FROM transfers WHERE (sender_id = ? OR receiver_id = ?) AND (transfer_status = 'TAMPERED' OR is_tampered = 1)",
        (user_id, user_id),
        one=True
    )
    pending = query_db(
        "SELECT COUNT(*) as count FROM transfers WHERE receiver_id = ? AND transfer_status = 'SENT'",
        (user_id,),
        one=True
    )

    recent_activities = query_db(
        '''
        SELECT * FROM audit_logs 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT 6
        ''',
        (user_id,)
    )

    return {
        "sent_count": sent['count'],
        "sent_bytes": sent['total_size'],
        "received_count": received['count'],
        "received_bytes": received['total_size'],
        "total_data_bytes": sent['total_size'] + received['total_size'],
        "successful_transfers": successful['count'],
        "failed_transfers": tampered['count'],
        "pending_count": pending['count'],
        "recent_activities": recent_activities
    }
