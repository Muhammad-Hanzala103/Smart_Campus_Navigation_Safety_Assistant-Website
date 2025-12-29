"""
Web Authentication Blueprint
Handles login, logout, registration, and password reset for web UI.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app.extensions import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle web login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()
        
        if user and user.password_hash and check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'error')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Handle logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not all([name, email, password]):
            flash('All fields are required.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please login.', 'error')
            return redirect(url_for('auth.login'))
        
        # Create user
        user = User(
            full_name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role='user',
            is_active=True
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password request."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            flash('Please enter your email address.', 'error')
            return render_template('forgot_password.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            # In dev mode, generate token and show it
            from app.services.email_service import generate_reset_token
            token = generate_reset_token(email)
            flash(f'Reset token (dev mode): {token}', 'info')
            return redirect(url_for('auth.reset_password', token=token, email=email))
        else:
            # Don't reveal if email exists
            flash('If the email exists, reset instructions will be sent.', 'info')
    
    return render_template('forgot_password.html')


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Handle password reset with token."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    
    token = request.args.get('token', '')
    email = request.args.get('email', '')
    
    if request.method == 'POST':
        token = request.form.get('token', '')
        email = request.form.get('email', '').strip().lower()
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if new_password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('reset_password.html', token=token, email=email)
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('reset_password.html', token=token, email=email)
        
        # Verify token
        from app.services.email_service import verify_reset_token
        try:
            token_email = verify_reset_token(token)
            if token_email.lower() != email:
                raise ValueError("Email mismatch")
        except Exception:
            flash('Invalid or expired reset token.', 'error')
            return redirect(url_for('auth.forgot_password'))
        
        # Update password
        user = User.query.filter_by(email=email).first()
        if user:
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            flash('Password reset successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('User not found.', 'error')
    
    return render_template('reset_password.html', token=token, email=email)
