import sqlite3
import os
from flask import g, current_app, has_app_context
from config import Config

def get_db():
    """Get or create SQLite connection for the current Flask application context."""
    if 'db' not in g:
        db_path = current_app.config.get('DATABASE_PATH', Config.DATABASE_PATH) if has_app_context() else Config.DATABASE_PATH
        # Ensure database directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        # Enable foreign key constraint enforcement
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db

def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    """Execute a SELECT query with parameters and return results as sqlite3.Row or list of Rows."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=(), commit=True):
    """Execute an INSERT, UPDATE, or DELETE query with parameters."""
    db = get_db()
    cur = db.execute(query, args)
    if commit:
        db.commit()
    lastrowid = cur.lastrowid
    cur.close()
    return lastrowid

def init_db(db_path=None):
    """Initialize SQLite database with required tables, constraints, and indices."""
    target_path = db_path or Config.DATABASE_PATH
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    
    conn = sqlite3.connect(target_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        public_key TEXT NOT NULL,
        encrypted_private_key TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    # Transfers Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transfers (
        transfer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        original_filename TEXT NOT NULL,
        encrypted_filename TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        encrypted_aes_key BLOB NOT NULL,
        nonce BLOB NOT NULL,
        auth_tag BLOB NOT NULL,
        original_sha256 TEXT NOT NULL,
        transfer_status TEXT NOT NULL DEFAULT 'SENT',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        decrypted_at TIMESTAMP,
        verified_sha256 TEXT,
        is_tampered INTEGER DEFAULT 0,
        FOREIGN KEY (sender_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (receiver_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    ''')

    # Login Attempts for Rate Limiting & Security Monitoring
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS login_attempts (
        attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip_address TEXT NOT NULL,
        username TEXT NOT NULL,
        attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        success INTEGER NOT NULL
    );
    ''')

    # Audit Logs Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS audit_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT NOT NULL,
        details TEXT NOT NULL,
        ip_address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
    );
    ''')

    # Create helpful indices for performance and security queries
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_transfers_sender ON transfers(sender_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_transfers_receiver ON transfers(receiver_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_login_attempts ON login_attempts(ip_address, attempt_time);')

    conn.commit()
    conn.close()
