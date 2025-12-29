from flask import Blueprint, render_template, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models import Incident, User, MapNode
from sqlalchemy import func
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def index():
    """Redirect to dashboard or login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    return redirect(url_for('auth.login'))


@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard view with statistics."""
    total_incidents = Incident.query.count()
    active_incidents = Incident.query.filter(
        Incident.status.in_(['new', 'under_review', 'escalated'])
    ).count()
    critical_incidents = Incident.query.filter(
        Incident.ai_severity.in_(['CRITICAL', 'HIGH'])
    ).count()

    recent_incidents = Incident.query.order_by(Incident.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                           total=total_incidents,
                           active=active_incidents,
                           critical=critical_incidents,
                           recent_incidents=recent_incidents)


@dashboard_bp.route('/incidents')
@login_required
def incidents():
    """Incident list view."""
    all_incidents = Incident.query.order_by(Incident.created_at.desc()).all()
    return render_template('incidents.html', incidents=all_incidents)


@dashboard_bp.route('/map')
@login_required
def map_view():
    """Map intelligence view."""
    incidents = Incident.query.filter(
        Incident.status.in_(['new', 'under_review', 'escalated'])
    ).all()
    nodes = MapNode.query.all()
    return render_template('map.html', incidents=incidents, nodes=nodes)


@dashboard_bp.route('/status')
@login_required  
def system_status():
    """System status page."""
    return render_template('status.html')
