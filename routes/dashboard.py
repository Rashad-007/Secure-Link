from flask import Blueprint, render_template, session, redirect, url_for
from routes.auth import login_required
from services.transfer_service import get_dashboard_statistics

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard_view'))
    return render_template('index.html')

@dashboard_bp.route('/dashboard')
@login_required
def dashboard_view():
    current_user_id = session['user_id']
    stats = get_dashboard_statistics(current_user_id)
    return render_template('dashboard.html', stats=stats)

@dashboard_bp.route('/security')
def security_view():
    return render_template('security.html')

