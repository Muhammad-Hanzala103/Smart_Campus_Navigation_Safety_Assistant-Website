from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify
from app.models import User, Incident, Booking, AuditLog, MapNode
from app import db, oauth
from app.utils import login_required, role_required, ROLE_ADMIN, ROLE_SECURITY, ROLE_STAFF, has_permission
from datetime import datetime

web_bp = Blueprint('web', __name__)

@web_bp.context_processor
def inject_permissions():
    """Make permissions available in all templates"""
    def check_permission(permission):
        return has_permission(session.get('user_role', 'student'), permission)
    return dict(has_permission=check_permission)

# ============== AUTH ==============
@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_role'] = user.role
            session['user_email'] = user.email
            # Log action
            log = AuditLog(user_id=user.id, action='LOGIN', details=f'User logged in from web')
            db.session.add(log)
            db.session.commit()
            return redirect(url_for('web.dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@web_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        
        if password != confirm:
            flash('Passwords do not match')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return render_template('register.html')
        
        user = User(name=name, email=email, role='student')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please login.')
        return redirect(url_for('web.login'))
    return render_template('register.html')

@web_bp.route('/logout')
def logout():
    if 'user_id' in session:
        log = AuditLog(user_id=session['user_id'], action='LOGOUT', details='User logged out')
        db.session.add(log)
        db.session.commit()
    session.clear()
    return redirect(url_for('web.login'))

# ============== GOOGLE OAUTH ==============
@web_bp.route('/login/google')
def google_login():
    redirect_uri = url_for('web.google_authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@web_bp.route('/login/google/authorize')
def google_authorize():
    token = oauth.google.authorize_access_token()
    user_info = token.get('userinfo')
    if not user_info:
        flash('Failed to fetch user info from Google')
        return redirect(url_for('web.login'))
    
    email = user_info['email']
    name = user_info['name']
    
    user = User.query.filter_by(email=email).first()
    if not user:
        # Create user if not exists
        user = User(name=name, email=email, role='student')
        db.session.add(user)
        db.session.commit()
        flash(f'Welcome {name}! Your account has been created via Google.')
    
    session['user_id'] = user.id
    session['user_name'] = user.name
    session['user_role'] = user.role
    session['user_email'] = user.email
    
    log = AuditLog(user_id=user.id, action='LOGIN_GOOGLE', details='User logged in via Google OAuth')
    db.session.add(log)
    db.session.commit()
    
    return redirect(url_for('web.dashboard'))

@web_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Password reset link sent to your email (demo mode)')
        else:
            flash('Email not found')
    return render_template('forgot_password.html')

# ============== DASHBOARD ==============
@web_bp.route('/dashboard')
@login_required
def dashboard():
    stats = {
        'high_risk': Incident.query.filter_by(ai_severity='HIGH').count(),
        'active_cases': Incident.query.filter_by(status='open').count(),
        'total_reports': Incident.query.count(),
        'total_users': User.query.count()
    }
    recent_incidents = Incident.query.order_by(Incident.created_at.desc()).limit(5).all()
    recent_activity = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()
    return render_template('dashboard.html', stats=stats, recent_incidents=recent_incidents, activity=recent_activity)

# ============== SECURITY MODULE ==============
@web_bp.route('/security')
@login_required
@role_required(ROLE_ADMIN, ROLE_SECURITY)
def security_dashboard():
    return render_template('security_dashboard.html')

# ============== FACULTY MODULE ==============
from app.models import Course, Shuttle # Import new models
@web_bp.route('/faculty')
@login_required
# @role_required(ROLE_ADMIN, ROLE_STAFF) # Loosened for demo
def faculty_dashboard():
    courses = Course.query.all()
    # If using user-specific courses: courses = Course.query.filter_by(instructor_id=session['user_id']).all()
    return render_template('faculty_dashboard.html', courses=courses)

# ============== TRANSPORT MODULE ==============
@web_bp.route('/transport')
@login_required
def transport_dashboard():
    shuttles = Shuttle.query.all()
    return render_template('transport_dashboard.html', shuttles=shuttles) # Pass shuttle data

# ============== LIBRARY MODULE ==============
from app.models import Book
@web_bp.route('/library')
@login_required
def library_dashboard():
    books = Book.query.all()
    return render_template('library_dashboard.html', books=books)

# ============== INCIDENTS ==============

# ============== INCIDENTS ==============
@web_bp.route('/incidents')
@login_required
def incidents():
    status_filter = request.args.get('status', '')
    severity_filter = request.args.get('severity', '')
    search = request.args.get('search', '')
    
    query = Incident.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if severity_filter:
        query = query.filter_by(ai_severity=severity_filter)
    if search:
        query = query.filter(Incident.description.ilike(f'%{search}%'))
    
    all_incidents = query.order_by(Incident.created_at.desc()).all()
    return render_template('incidents.html', incidents=all_incidents)

@web_bp.route('/incidents/<int:id>')
@login_required
def incident_detail(id):
    incident = Incident.query.get_or_404(id)
    return render_template('incident_detail.html', incident=incident)

@web_bp.route('/incidents/<int:id>/status', methods=['POST'])
@role_required(ROLE_ADMIN, ROLE_SECURITY)
def update_incident_status(id):
    incident = Incident.query.get_or_404(id)
    new_status = request.form.get('status')
    if new_status in ['open', 'in_progress', 'resolved', 'closed']:
        old_status = incident.status
        incident.status = new_status
        log = AuditLog(user_id=session['user_id'], action='INCIDENT_STATUS_CHANGE', 
                      details=f'Incident #{id} status: {old_status} → {new_status}')
        db.session.add(log)
        db.session.commit()
        flash(f'Incident status updated to {new_status}')
    return redirect(url_for('web.incident_detail', id=id))

# ============== MAP INTELLIGENCE ==============
@web_bp.route('/map-intelligence')
@login_required
def map_intelligence():
    return render_template('map_intelligence.html')

# ============== SYSTEM STATUS ==============
@web_bp.route('/system-status')
@login_required
def system_status():
    return render_template('system_status.html')

# ============== USERS (Admin Only) ==============
@web_bp.route('/users')
@role_required(ROLE_ADMIN)
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('users.html', users=all_users)

@web_bp.route('/users/<int:id>/role', methods=['POST'])
@role_required(ROLE_ADMIN)
def update_user_role(id):
    user = User.query.get_or_404(id)
    new_role = request.form.get('role')
    if new_role in ['admin', 'security', 'staff', 'student']:
        old_role = user.role
        user.role = new_role
        log = AuditLog(user_id=session['user_id'], action='USER_ROLE_CHANGE',
                      details=f'User {user.email} role: {old_role} → {new_role}')
        db.session.add(log)
        db.session.commit()
        flash(f'User role updated to {new_role}')
    return redirect(url_for('web.users'))

# ============== ANALYTICS ==============
@web_bp.route('/analytics')
@role_required(ROLE_ADMIN, ROLE_SECURITY)
def analytics():
    return render_template('analytics.html')

# ============== AUDIT LOGS (Admin Only) ==============
@web_bp.route('/audit-logs')
@role_required(ROLE_ADMIN)
def audit_logs():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    return render_template('audit_logs.html', logs=logs)

# ============== SETTINGS ==============
@web_bp.route('/settings')
@role_required(ROLE_ADMIN)
def settings():
    return render_template('settings.html')

# ============== PROFILE ==============
@web_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.name = request.form.get('name', user.name)
        user.phone = request.form.get('phone', user.phone)
        if request.form.get('new_password'):
            if user.check_password(request.form.get('current_password', '')):
                user.set_password(request.form.get('new_password'))
                flash('Password updated successfully')
            else:
                flash('Current password is incorrect')
                return render_template('profile.html', user=user)
        db.session.commit()
        session['user_name'] = user.name
        flash('Profile updated successfully')
    return render_template('profile.html', user=user)

# ============== API ENDPOINTS FOR AJAX ==============
@web_bp.route('/api/incidents/stats')
@login_required
def incident_stats():
    return jsonify({
        'total': Incident.query.count(),
        'open': Incident.query.filter_by(status='open').count(),
        'in_progress': Incident.query.filter_by(status='in_progress').count(),
        'resolved': Incident.query.filter_by(status='resolved').count(),
        'high': Incident.query.filter_by(ai_severity='HIGH').count(),
        'medium': Incident.query.filter_by(ai_severity='MEDIUM').count(),
        'low': Incident.query.filter_by(ai_severity='LOW').count()
    })

@web_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('web.dashboard'))
    return render_template('index.html')

@web_bp.route('/sitemap.xml')
def sitemap():
    """Generate sitemap.xml for SEO"""
    from flask import make_response
    pages = []
    # Static pages
    pages.append(["http://ciias-web.vercel.app/", "2024-01-01"])
    pages.append(["http://ciias-web.vercel.app/login", "2024-01-01"])
    pages.append(["http://ciias-web.vercel.app/register", "2024-01-01"])
    
    xml_sitemap = render_template('sitemap.xml', pages=pages)
    response = make_response(xml_sitemap)
    response.headers["Content-Type"] = "application/xml"
    return response

# ============== CAFETERIA MODULE ==============
from app.models import CafeteriaItem, CafeteriaOrder
@web_bp.route('/cafeteria')
@login_required
def cafeteria_dashboard():
    items = CafeteriaItem.query.all()
    # For demo, fetch recent orders
    orders = CafeteriaOrder.query.order_by(CafeteriaOrder.created_at.desc()).limit(10).all()
    return render_template('cafeteria_dashboard.html', items=items, orders=orders)

# ============== FINANCIAL MODULE ==============
from app.models import Wallet, FeeChallan
@web_bp.route('/financial')
@login_required
def financial_dashboard():
    # Ensure user has a wallet
    wallet = Wallet.query.get(session['user_id'])
    if not wallet:
        wallet = Wallet(user_id=session['user_id'], balance=0)
        db.session.add(wallet)
        db.session.commit()
    
    challans = FeeChallan.query.filter_by(user_id=session['user_id']).all()
    return render_template('financial_dashboard.html', wallet=wallet, challans=challans)

# ============== CHAT MODULE ==============
from app.models import ChatMessage
@web_bp.route('/chat')
@login_required
def chat_dashboard():
    # Get recent contacts (users who have chatted with current user)
    # Simplified: Get all users except current
    users = User.query.filter(User.id != session['user_id']).all()
    return render_template('chat.html', contacts=users)
