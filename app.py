import os
from flask import Flask, render_template
from config import Config
from database.db import close_db, init_db
from routes.auth import auth_bp
from routes.transfer import transfer_bp
from routes.dashboard import dashboard_bp

def format_file_size(size_in_bytes):
    """Format bytes into human-readable B, KB, MB, GB."""
    if size_in_bytes is None:
        return "0 B"
    size = float(size_in_bytes)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}" if unit != 'B' else f"{int(size)} B"
        size /= 1024.0
    return f"{size:.2f} TB"

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize SQLite database
    with app.app_context():
        init_db()

    # Ensure storage directory exists
    os.makedirs(app.config['STORAGE_DIR'], exist_ok=True)

    # Teardown database connection
    app.teardown_appcontext(close_db)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(transfer_bp)
    app.register_blueprint(dashboard_bp)

    # Custom Jinja Template Filters
    app.jinja_env.filters['filesize'] = format_file_size

    # Security Headers Middleware
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

    # Error Handlers
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('base.html', content="<div class='container py-5 text-center text-danger'><h2>403 - Forbidden</h2><p>You do not have permission to access this resource.</p></div>"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('base.html', content="<div class='container py-5 text-center text-warning'><h2>404 - Not Found</h2><p>The requested page or resource could not be found.</p></div>"), 404

    @app.errorhandler(413)
    def payload_too_large(e):
        return render_template('base.html', content=f"<div class='container py-5 text-center text-danger'><h2>413 - Payload Too Large</h2><p>Uploaded file exceeds maximum limit of {Config.MAX_CONTENT_LENGTH // (1024*1024)}MB.</p></div>"), 413

    @app.errorhandler(500)
    def internal_error(e):
        return render_template('base.html', content="<div class='container py-5 text-center text-danger'><h2>500 - Internal Server Error</h2><p>An unexpected cryptographic or system error occurred.</p></div>"), 500

    return app

app = create_app()

if __name__ == '__main__':
    # Run locally or accessible via local network for multi-device testing
    port = int(os.environ.get('PORT', 5000))
    print(f"[*] Starting SecureLink Server on http://0.0.0.0:{port}")
    print(f"[*] Access locally at: http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)

