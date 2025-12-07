import smtplib
import sqlite3
import secrets
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv

DB_PATH = os.getenv("DB_PATH", "database/otakuzone.db")

load_dotenv()

# Import email configuration
try:
    from config.email_config import (
        EMAIL_HOST,
        EMAIL_PORT,
        EMAIL_ADDRESS,
        EMAIL_PASSWORD,
    )
    print(f"Email config loaded: {EMAIL_ADDRESS}")
except ImportError as e:
    print(f"Failed to import email config: {e}")
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_PORT = 587
    EMAIL_ADDRESS = None
    EMAIL_PASSWORD = None


# ===== CODE GENERATION =====

def generate_verification_code():
    """Generate a 6-digit verification code"""
    return str(secrets.randbelow(900000) + 100000)

def generate_reset_code():
    """Generate a 6-digit reset code"""
    return str(secrets.randbelow(900000) + 100000)


# ===== DATABASE FUNCTIONS =====

def store_verification_code(email, code):
    """Store verification code in database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS verification_codes (
            email TEXT PRIMARY KEY,
            code TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Delete old code if exists
    cursor.execute("DELETE FROM verification_codes WHERE email = ?", (email,))
    
    # Insert new code
    cursor.execute("""
        INSERT INTO verification_codes (email, code, created_at)
        VALUES (?, ?, ?)
    """, (email, code, datetime.now()))
    
    conn.commit()
    conn.close()

def verify_code(email, code):
    """Verify if code is correct and not expired (10 minutes)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT code, created_at FROM verification_codes
        WHERE email = ?
    """, (email,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return False
    
    stored_code, created_at = result
    created_time = datetime.fromisoformat(created_at)
    
    # Check if expired (10 minutes)
    if datetime.now() - created_time > timedelta(minutes=10):
        return False
    
    return stored_code == code

def clear_verification_code(email):
    """Clear verification code after successful verification"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM verification_codes WHERE email = ?", (email,))
    conn.commit()
    conn.close()


# ===== EMAIL SENDING =====

def send_email(to_email, subject, body_html):
    """Generic email sending function"""
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject
        
        html_part = MIMEText(body_html, 'html')
        msg.attach(html_part)
        
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=30) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        
        return True, None
    except Exception as e:
        return False, str(e)


# ===== EMAIL TEMPLATES =====

def send_verification_email(email, name, code):
    """Send email verification code during signup"""
    subject = "OtakuZone - Verify Your Email"
    
    body_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="text-align: center;  max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px;">
                <h2 style="color: #E50914;">Welcome to OtakuZone, {name}! 🎌</h2>
                <p style="font-size: 16px; color: #333;">Thank you for signing up!</p>
                <p style="font-size: 16px; color: #333;">Your verification code is:</p>
                <div style="background-color: #f0f0f0; padding: 20px; text-align: center; border-radius: 5px; margin: 20px 0;">
                    <h1 style="color: #E50914; font-size: 36px; margin: 0; letter-spacing: 5px;">{code}</h1>
                </div>
                <p style="font-size: 14px; color: #666;">This code will expire in 10 minutes.</p>
                <p style="font-size: 14px; color: #666;">If you didn't request this, please ignore this email.</p>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                <p style="font-size: 12px; color: #999;">OtakuZone - Your Anime Streaming Platform</p>
            </div>
        </body>
    </html>
    """
    
    store_verification_code(email, code)
    return send_email(email, subject, body_html)

def send_admin_user_verification_email(email, code):
    """Send email verification code when admin creates a user"""
    subject = "OtakuZone - Account Created - Verify Your Email"
    
    body_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style=" text-align: center;  max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px;">
                <h2 style="color: #E50914;">Welcome to OtakuZone! 🎌</h2>
                <p style="font-size: 16px; color: #333;">An admin has created an account for you.</p>
                <p style="font-size: 16px; color: #333;">Your verification code is:</p>
                <div style="background-color: #f0f0f0; padding: 20px; text-align: center; border-radius: 5px; margin: 20px 0;">
                    <h1 style="color: #E50914; font-size: 36px; margin: 0; letter-spacing: 5px;">{code}</h1>
                </div>
                <p style="font-size: 14px; color: #666;">This code will expire in 10 minutes.</p>
                <p style="font-size: 14px; color: #666;">If you didn't expect this, please contact an administrator.</p>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                <p style="font-size: 12px; color: #999;">OtakuZone - Your Anime Streaming Platform</p>
            </div>
        </body>
    </html>
    """
    
    store_verification_code(email, code)
    return send_email(email, subject, body_html)

def send_password_reset_email(email, code):
    """Send password reset code"""
    subject = "OtakuZone - Password Reset Code"
    
    body_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="text-align: center;  max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px;">
                <h2 style="color: #E50914;">Password Reset Request 🔐</h2>
                <p style="font-size: 16px; color: #333;">You requested to reset your password.</p>
                <p style="font-size: 16px; color: #333;">Your reset code is:</p>
                <div style="background-color: #f0f0f0; padding: 20px; text-align: center; border-radius: 5px; margin: 20px 0;">
                    <h1 style="color: #E50914; font-size: 36px; margin: 0; letter-spacing: 5px;">{code}</h1>
                </div>
                <p style="font-size: 14px; color: #666;">This code will expire in 10 minutes.</p>
                <p style="font-size: 14px; color: #666;">If you didn't request this, please ignore this email.</p>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                <p style="font-size: 12px; color: #999;">OtakuZone - Your Anime Streaming Platform</p>
            </div>
        </body>
    </html>
    """
    
    store_verification_code(email, code)
    return send_email(email, subject, body_html)

def send_2fa_code_email(email, code):
    """Send 2FA verification code"""
    subject = "OtakuZone - Two-Factor Authentication Code"
    
    body_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="text-align: center; max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px;">
                <h2 style="color: #E50914;">Two-Factor Authentication 🔐</h2>
                <p style="font-size: 16px; color: #333;">Someone is trying to log in to your account.</p>
                <p style="font-size: 16px; color: #333;">Your authentication code is:</p>
                <div style="background-color: #f0f0f0; padding: 20px; text-align: center; border-radius: 5px; margin: 20px 0;">
                    <h1 style="color: #E50914; font-size: 36px; margin: 0; letter-spacing: 5px;">{code}</h1>
                </div>
                <p style="font-size: 14px; color: #666;">This code will expire in 10 minutes.</p>
                <p style="font-size: 14px; color: #666;">If you didn't try to log in, please secure your account immediately.</p>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                <p style="font-size: 12px; color: #999;">OtakuZone - Your Anime Streaming Platform</p>
            </div>
        </body>
    </html>
    """
    
    store_verification_code(email, code)
    return send_email(email, subject, body_html)


# Legacy function names for compatibility
def send_verification_code_email(recipient_email, code, name):
    """Legacy function - redirects to send_verification_email"""
    return send_verification_email(recipient_email, name, code)

def send_reset_code_email(recipient_email, reset_code):
    """Legacy function - redirects to send_password_reset_email"""
    return send_password_reset_email(recipient_email, reset_code)