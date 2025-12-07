import sqlite3
from datetime import datetime, timedelta
import bcrypt
from services.email_service import generate_reset_code, send_reset_code_email
import os
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "database/otakuzone.db")


def create_reset_codes_table():
    """Create table to store password reset codes"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_reset_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            code TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            used INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def user_exists(email):
    """Check if user exists with given email"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user is not None


def send_reset_code(email):
    """
    Generate and send reset code to user's email
    Returns: (success: bool, message: str)
    """
    print(f"\nChecking if user exists: {email}")
    
    # Check if user exists
    if not user_exists(email):
        print(f"User not found: {email}")
        # Return error message (not revealing if email exists is less secure but more user-friendly)
        return False, "Email not found. Please check your email or sign up."
    
    print(f"User found: {email}")
    
    # Generate code
    reset_code = generate_reset_code()
    print(f"Generated code: {reset_code}")
    
    # Save to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Delete old unused codes for this email
    cursor.execute("""
        DELETE FROM password_reset_codes 
        WHERE email = ? AND used = 0
    """, (email,))
    print(f"Deleted old codes for: {email}")
    
    # Create new code
    created_at = datetime.now().isoformat()
    expires_at = (datetime.now() + timedelta(minutes=10)).isoformat()
    
    cursor.execute("""
        INSERT INTO password_reset_codes (email, code, created_at, expires_at)
        VALUES (?, ?, ?, ?)
    """, (email, reset_code, created_at, expires_at))
    print(f"Saved code to database")
    
    conn.commit()
    conn.close()
    
    # Send email
    print(f"Attempting to send email...")
    success, error = send_reset_code_email(email, reset_code)
    
    if success:
        print(f"Email sent successfully!")
        return True, "Reset code sent to your email. Check your inbox."
    else:
        print(f"Email failed: {error}")
        return False, f"Failed to send email: {error}"


def verify_reset_code(email, code):
    """
    Verify if reset code is valid
    Returns: (valid: bool, message: str)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get the latest unused code for this email
    cursor.execute("""
        SELECT id, expires_at FROM password_reset_codes
        WHERE email = ? AND code = ? AND used = 0
        ORDER BY created_at DESC
        LIMIT 1
    """, (email, code))
    
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return False, "Invalid or expired code."
    
    code_id, expires_at = result
    
    # Check if expired
    if datetime.now() > datetime.fromisoformat(expires_at):
        conn.close()
        return False, "Code has expired. Please request a new one."
    
    conn.close()
    return True, "Code verified successfully."


def reset_password(email, code, new_password):
    """
    Reset password after verifying code
    Returns: (success: bool, message: str)
    """
    # Verify code first
    valid, message = verify_reset_code(email, code)
    if not valid:
        return False, message
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Hash new password
    hashed_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
    
    # Update password
    cursor.execute("""
        UPDATE users SET password = ? WHERE email = ?
    """, (hashed_pw, email))
    
    # Mark code as used
    cursor.execute("""
        UPDATE password_reset_codes 
        SET used = 1 
        WHERE email = ? AND code = ?
    """, (email, code))
    
    conn.commit()
    conn.close()
    
    return True, "Password reset successfully!"


# Initialize table on import
create_reset_codes_table()