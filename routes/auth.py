import re
from functools import wraps
from datetime import datetime, timezone, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g, current_app
from config import Config
from database.db import query_db, execute_db
from crypto.hashing import hash_user_password, verify_user_password, compute_sha256_bytes
from services.key_management import create_user_keys

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Authentication required. Please log in to access this page.", "warning")
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def is_rate_limited(ip_address: str, username: str) -> bool:
    """
    Check if too many failed login attempts have occurred within the lockout window.
    """
    lockout_mins = current_app.config.get('LOGIN_LOCKOUT_MINUTES', Config.LOGIN_LOCKOUT_MINUTES)
    max_attempts = current_app.config.get('MAX_FAILED_LOGIN_ATTEMPTS', Config.MAX_FAILED_LOGIN_ATTEMPTS)
    
    # SQLite CURRENT_TIMESTAMP is UTC
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=lockout_mins)
    cutoff_str = cutoff.strftime('%Y-%m-%d %H:%M:%S')

    recent_failures = query_db(
        '''
        SELECT COUNT(*) as count FROM login_attempts 
        WHERE (ip_address = ? OR username = ?) 
          AND success = 0 
          AND attempt_time > ?
        ''',
        (ip_address, username, cutoff_str),
        one=True
    )
    return recent_failures['count'] >= max_attempts

def validate_registration_input(username, email, password, confirm_password):
    if not username or not email or not password:
        return "All fields are required."
    if len(username) < 3 or len(username) > 30:
        return "Username must be between 3 and 30 characters."
    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        return "Username may only contain letters, numbers, hyphens, and underscores."
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        return "Please provide a valid email address."
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if password != confirm_password:
        return "Passwords do not match."
    return None

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard_view'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        error = validate_registration_input(username, email, password, confirm_password)
        if error:
            flash(error, "danger")
            return render_template('register.html', username=username, email=email)

        # Check existing username or email
        existing_user = query_db("SELECT user_id FROM users WHERE username = ? OR email = ?", (username, email), one=True)
        if existing_user:
            flash("Username or email is already registered.", "danger")
            return render_template('register.html', username=username, email=email)

        try:
            # 1. Generate RSA-3072 key pair and encrypt private key with password
            public_pem, enc_private_pem = create_user_keys(password)
            password_hash = hash_user_password(password)

            # 2. Insert user into database
            user_id = execute_db(
                '''
                INSERT INTO users (username, email, password_hash, public_key, encrypted_private_key)
                VALUES (?, ?, ?, ?, ?)
                ''',
                (username, email, password_hash, public_pem, enc_private_pem)
            )

            # 3. Log audit action
            execute_db(
                '''
                INSERT INTO audit_logs (user_id, action, details, ip_address)
                VALUES (?, 'USER_REGISTERED', 'User account registered with RSA-3072 key pair.', ?)
                ''',
                (user_id, request.remote_addr)
            )

            flash("Registration successful! Your RSA-3072 cryptographic key pair has been generated. Please log in.", "success")
            return redirect(url_for('auth.login'))

        except Exception as e:
            flash(f"Registration error: {str(e)}", "danger")
            return render_template('register.html', username=username, email=email)

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard_view'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        ip_addr = request.remote_addr

        # Rate limiting check
        if is_rate_limited(ip_addr, username):
            flash(f"Account locked temporarily due to too many failed attempts. Try again in {Config.LOGIN_LOCKOUT_MINUTES} minutes.", "danger")
            return render_template('login.html', username=username)

        user = query_db("SELECT * FROM users WHERE username = ? OR email = ?", (username, username), one=True)

        if user and verify_user_password(user['password_hash'], password):
            # Record successful login attempt
            execute_db(
                "INSERT INTO login_attempts (ip_address, username, success) VALUES (?, ?, 1)",
                (ip_addr, username)
            )

            # Set session
            session.clear()
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['email'] = user['email']

            execute_db(
                "INSERT INTO audit_logs (user_id, action, details, ip_address) VALUES (?, 'USER_LOGIN', 'User authenticated successfully.', ?)",
                (user['user_id'], ip_addr)
            )

            flash(f"Welcome back, {user['username']}! Session authenticated.", "success")
            next_url = request.args.get('next')
            return redirect(next_url or url_for('dashboard.dashboard_view'))
        else:
            # Record failed login attempt
            execute_db(
                "INSERT INTO login_attempts (ip_address, username, success) VALUES (?, ?, 0)",
                (ip_addr, username)
            )
            flash("Invalid credentials. Please verify your username and password.", "danger")
            return render_template('login.html', username=username)

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id:
        execute_db(
            "INSERT INTO audit_logs (user_id, action, details, ip_address) VALUES (?, 'USER_LOGOUT', 'User logged out.', ?)",
            (user_id, request.remote_addr)
        )
    session.clear()
    flash("You have been securely logged out.", "info")
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    user = query_db("SELECT * FROM users WHERE user_id = ?", (session['user_id'],), one=True)
    # Calculate SHA-256 fingerprint of the public key
    pubkey_fingerprint = compute_sha256_bytes(user['public_key'].encode('utf-8'))
    return render_template('profile.html', user=user, fingerprint=pubkey_fingerprint)
