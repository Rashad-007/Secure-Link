import io
from flask import (
    Blueprint, render_template, request, redirect, url_for, 
    flash, session, send_file, abort
)
from config import Config
from database.db import query_db, execute_db
from routes.auth import login_required
from services.encryption_service import process_and_encrypt_upload
from services.transfer_service import (
    get_transfer_by_id,
    check_transfer_authorization,
    decrypt_and_verify_transfer,
    simulate_tampering_attack
)

transfer_bp = Blueprint('transfer', __name__)

@transfer_bp.route('/send', methods=['GET', 'POST'])
@login_required
def send_file_view():
    current_user_id = session['user_id']

    if request.method == 'POST':
        receiver_id = request.form.get('receiver_id', type=int)
        file = request.files.get('file')

        if not receiver_id:
            flash("Please select a valid recipient for the encrypted transfer.", "danger")
            return redirect(url_for('transfer.send_file_view'))

        if not file or file.filename == '':
            flash("Please choose a file to encrypt and send.", "danger")
            return redirect(url_for('transfer.send_file_view'))

        try:
            result = process_and_encrypt_upload(
                file,
                sender_id=current_user_id,
                receiver_id=receiver_id,
                client_ip=request.remote_addr
            )
            flash(
                f"File '{result['original_filename']}' encrypted with AES-256-GCM and dispatched! SHA-256: {result['original_sha256'][:16]}...",
                "success"
            )
            return redirect(url_for('transfer.history_view'))

        except Exception as e:
            flash(f"Encryption & Transfer failed: {str(e)}", "danger")
            return redirect(url_for('transfer.send_file_view'))

    # GET: fetch list of available registered recipients (excluding self)
    recipients = query_db(
        "SELECT user_id, username, email FROM users WHERE user_id != ? ORDER BY username ASC",
        (current_user_id,)
    )
    return render_template('send.html', recipients=recipients)

@transfer_bp.route('/received')
@login_required
def received_view():
    current_user_id = session['user_id']
    query = '''
    SELECT t.*, s.username AS sender_username, s.email AS sender_email
    FROM transfers t
    JOIN users s ON t.sender_id = s.user_id
    WHERE t.receiver_id = ?
    ORDER BY t.created_at DESC
    '''
    transfers = query_db(query, (current_user_id,))
    return render_template('received.html', transfers=transfers)

@transfer_bp.route('/history')
@login_required
def history_view():
    current_user_id = session['user_id']
    filter_type = request.args.get('filter', 'all')

    base_query = '''
    SELECT t.*, 
           s.username AS sender_username, 
           r.username AS receiver_username
    FROM transfers t
    JOIN users s ON t.sender_id = s.user_id
    JOIN users r ON t.receiver_id = r.user_id
    '''
    
    if filter_type == 'sent':
        query = base_query + " WHERE t.sender_id = ? ORDER BY t.created_at DESC"
        params = (current_user_id,)
    elif filter_type == 'received':
        query = base_query + " WHERE t.receiver_id = ? ORDER BY t.created_at DESC"
        params = (current_user_id,)
    else:
        query = base_query + " WHERE t.sender_id = ? OR t.receiver_id = ? ORDER BY t.created_at DESC"
        params = (current_user_id, current_user_id)

    transfers = query_db(query, params)
    return render_template('history.html', transfers=transfers, current_filter=filter_type)

@transfer_bp.route('/decrypt/<int:transfer_id>', methods=['GET', 'POST'])
@login_required
def decrypt_view(transfer_id):
    current_user_id = session['user_id']
    transfer = get_transfer_by_id(transfer_id)
    
    if not transfer:
        flash("Transfer record not found.", "danger")
        return redirect(url_for('transfer.received_view'))

    try:
        check_transfer_authorization(transfer, current_user_id)
    except PermissionError as e:
        flash(str(e), "danger")
        return redirect(url_for('dashboard.dashboard_view'))

    # If user is sender, they can view details but cannot decrypt as receiver
    is_receiver = (transfer['receiver_id'] == current_user_id)

    decryption_result = None

    if request.method == 'POST':
        if not is_receiver:
            flash("Only the intended recipient holds the private RSA key to decrypt this file.", "danger")
            return redirect(url_for('transfer.decrypt_view', transfer_id=transfer_id))

        password = request.form.get('password', '')
        if not password:
            flash("Please enter your account password to unlock your RSA-3072 private key.", "danger")
            return render_template('decrypt.html', transfer=transfer, is_receiver=is_receiver)

        try:
            result = decrypt_and_verify_transfer(
                transfer_id=transfer_id,
                user_id=current_user_id,
                password=password,
                client_ip=request.remote_addr
            )
            decryption_result = result
            # Store in session temporary token for one-time direct download
            session[f'decrypted_{transfer_id}'] = True
            flash("File successfully decrypted and SHA-256 integrity verified!", "success")
            # Refresh transfer record
            transfer = get_transfer_by_id(transfer_id)

        except Exception as e:
            flash(f"Decryption / Verification Alert: {str(e)}", "danger")
            transfer = get_transfer_by_id(transfer_id)

    return render_template(
        'decrypt.html', 
        transfer=transfer, 
        is_receiver=is_receiver, 
        result=decryption_result
    )

@transfer_bp.route('/download/decrypted/<int:transfer_id>', methods=['POST'])
@login_required
def download_decrypted(transfer_id):
    """Download decrypted plaintext file after password verification."""
    current_user_id = session['user_id']
    transfer = get_transfer_by_id(transfer_id)
    
    if not transfer or transfer['receiver_id'] != current_user_id:
        abort(403)

    password = request.form.get('password', '')
    if not password:
        flash("Password required to decrypt and download file.", "danger")
        return redirect(url_for('transfer.decrypt_view', transfer_id=transfer_id))

    try:
        result = decrypt_and_verify_transfer(
            transfer_id=transfer_id,
            user_id=current_user_id,
            password=password,
            client_ip=request.remote_addr
        )

        return send_file(
            io.BytesIO(result['plaintext']),
            as_attachment=True,
            download_name=result['filename'],
            mimetype='application/octet-stream'
        )

    except Exception as e:
        flash(f"Decryption failed: {str(e)}", "danger")
        return redirect(url_for('transfer.decrypt_view', transfer_id=transfer_id))

@transfer_bp.route('/download/encrypted/<int:transfer_id>')
@login_required
def download_encrypted(transfer_id):
    """Download raw ciphertext file (.enc) directly from storage."""
    current_user_id = session['user_id']
    transfer = get_transfer_by_id(transfer_id)
    
    if not transfer:
        abort(404)
        
    check_transfer_authorization(transfer, current_user_id)
    
    import os
    enc_path = os.path.join(Config.STORAGE_DIR, transfer['encrypted_filename'])
    if not os.path.exists(enc_path):
        flash("Encrypted file not found on disk.", "danger")
        return redirect(url_for('transfer.history_view'))

    return send_file(
        enc_path,
        as_attachment=True,
        download_name=transfer['encrypted_filename'],
        mimetype='application/octet-stream'
    )

@transfer_bp.route('/tamper/<int:transfer_id>', methods=['POST'])
@login_required
def tamper_view(transfer_id):
    """Academic demonstration endpoint: Corrupt ciphertext on disk to test GCM detection."""
    current_user_id = session['user_id']
    try:
        simulate_tampering_attack(transfer_id, current_user_id, request.remote_addr)
        flash("LAB ATTACK SIMULATED: Encrypted payload bytes on the server were modified. Now attempt decryption to observe AES-256-GCM authentication failure!", "warning")
    except Exception as e:
        flash(f"Could not simulate tamper attack: {str(e)}", "danger")

    return redirect(url_for('transfer.decrypt_view', transfer_id=transfer_id))

