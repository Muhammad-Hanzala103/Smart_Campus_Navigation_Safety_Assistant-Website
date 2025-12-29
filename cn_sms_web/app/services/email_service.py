"""
Email Service for Password Reset
Handles sending password reset emails or returning tokens in dev mode.
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
from itsdangerous import URLSafeTimedSerializer
import logging

logger = logging.getLogger(__name__)


def get_reset_token_serializer():
    """Get serializer for generating time-limited reset tokens."""
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])


def generate_reset_token(email: str) -> str:
    """
    Generate a time-limited password reset token.
    
    Args:
        email: User's email address
    
    Returns:
        Signed token string (valid for 1 hour)
    """
    serializer = get_reset_token_serializer()
    return serializer.dumps(email, salt='password-reset')


def verify_reset_token(token: str, max_age: int = 3600) -> str:
    """
    Verify a password reset token.
    
    Args:
        token: The reset token
        max_age: Maximum age in seconds (default 1 hour)
    
    Returns:
        Email address if valid
    
    Raises:
        SignatureExpired: If token has expired
        BadSignature: If token is invalid
    """
    serializer = get_reset_token_serializer()
    return serializer.loads(token, salt='password-reset', max_age=max_age)


def send_reset_email(email: str, token: str, reset_url: str) -> bool:
    """
    Send password reset email.
    
    Args:
        email: Recipient email
        token: Reset token
        reset_url: Full URL for password reset page
    
    Returns:
        True if sent successfully, False otherwise
    """
    if current_app.config.get('PASSWORD_RESET_DEV_MODE'):
        logger.info(f"DEV MODE: Reset token for {email}: {token}")
        return True
    
    try:
        smtp_host = current_app.config['SMTP_HOST']
        smtp_port = current_app.config['SMTP_PORT']
        smtp_user = current_app.config['SMTP_USER']
        smtp_pass = current_app.config['SMTP_PASS']
        smtp_from = current_app.config['SMTP_FROM']
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'CNSMS Password Reset Request'
        msg['From'] = smtp_from
        msg['To'] = email
        
        text_content = f"""
CNSMS Password Reset

You have requested to reset your password.
Click the link below or copy it to your browser:

{reset_url}

This link will expire in 1 hour.

If you did not request this reset, please ignore this email.

- CNSMS Security Team
        """
        
        html_content = f"""
<html>
<body style="font-family: Arial, sans-serif; padding: 20px;">
    <h2>CNSMS Password Reset</h2>
    <p>You have requested to reset your password.</p>
    <p>
        <a href="{reset_url}" 
           style="background: #1e40af; color: white; padding: 12px 24px; 
                  text-decoration: none; border-radius: 6px; display: inline-block;">
            Reset Password
        </a>
    </p>
    <p style="margin-top: 20px; color: #666;">
        Or copy this link: <br>
        <code>{reset_url}</code>
    </p>
    <p style="color: #999; font-size: 12px;">
        This link expires in 1 hour. If you did not request this reset, please ignore this email.
    </p>
</body>
</html>
        """
        
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        
        logger.info(f"Reset email sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send reset email to {email}: {e}")
        return False
