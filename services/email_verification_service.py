import sqlite3
import json
from datetime import datetime, timedelta
from services.email_service import generate_reset_code, send_verification_code_email
import os
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "database/otakuzone.db")


def create_verification_table():
    """Create table to store email verification codes"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_verification_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            code TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            used INTEGER DEFAULT 0,
            user_data TEXT
        )
    """)
    conn.commit()
    conn.close()


def email_already_registered(email):
    """Check if email is already registered and verified"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, email_verified FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return True
    return False


def username_already_exists(username):
    """Check if username is already taken"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def send_verification_code(email, user_data):
    """
    Generate and send verification code to user's email
    user_data: dict with name, username, password
    Returns: (success: bool, message: str)
    """
    print(f"\nEmail Verification: Checking email: {email}")
    
    # Check if email already registered
    if email_already_registered(email):
        print(f"Email Verification: Email already exists: {email}")
        return False, "Email already registered. Please use login."
    
    # Check if username already exists
    if username_already_exists(user_data['username']):
        print(f"Email Verification: Username already exists: {user_data['username']}")
        return False, "Username already taken. Please choose another."
    
    print(f"Email Verification: Email available: {email}")
    
    # Generate code
    code = generate_reset_code()
    print(f"Email Verification: Generated code: {code}")
    
    # Save to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Delete old unused codes for this email
    cursor.execute("""
        DELETE FROM email_verification_codes 
        WHERE email = ? AND used = 0
    """, (email,))
    print(f"Email Verification: Deleted old codes for: {email}")
    
    # Create new code
    created_at = datetime.now().isoformat()
    expires_at = (datetime.now() + timedelta(minutes=10)).isoformat()
    user_data_json = json.dumps(user_data)
    
    cursor.execute("""
        INSERT INTO email_verification_codes (email, code, created_at, expires_at, user_data)
        VALUES (?, ?, ?, ?, ?)
    """, (email, code, created_at, expires_at, user_data_json))
    print(f"Email Verification: Saved code to database")
    
    conn.commit()
    conn.close()
    
    # Send email
    print(f"Email Verification: Attempting to send email...")
    success, error = send_verification_code_email(email, code, user_data['name'])
    
    if success:
        print(f"Email Verification: Email sent successfully!")
        return True, "Verification code sent to your email. Please check your inbox."
    else:
        print(f"Email Verification: Email failed: {error}")
        return False, f"Failed to send verification email: {error}"


def verify_code_and_create_account(email, code):
    """
    Verify code and create user account if valid
    Returns: (success: bool, message: str)
    """
    import bcrypt
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get the latest unused code for this email
    cursor.execute("""
        SELECT id, expires_at, user_data FROM email_verification_codes
        WHERE email = ? AND code = ? AND used = 0
        ORDER BY created_at DESC
        LIMIT 1
    """, (email, code))
    
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return False, "Invalid or expired verification code."
    
    code_id, expires_at, user_data_json = result
    
    # Check if expired
    if datetime.now() > datetime.fromisoformat(expires_at):
        conn.close()
        return False, "Verification code has expired. Please request a new one."
    
    # Parse user data
    user_data = json.loads(user_data_json)
    
    # Check if email still available
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return False, "Email already registered. Please use login."
    
    # Check if username still available
    cursor.execute("SELECT id FROM users WHERE username = ?", (user_data['username'],))
    if cursor.fetchone():
        conn.close()
        return False, "Username already taken. Please sign up again with a different username."
    
    # Hash password
    hashed_pw = bcrypt.hashpw(user_data['password'].encode("utf-8"), bcrypt.gensalt())
    
    # Create user account
    cursor.execute("""
        INSERT INTO users (name, username, email, password, email_verified)
        VALUES (?, ?, ?, ?, 1)
    """, (user_data['name'], user_data['username'], email, hashed_pw))
    
    # Mark code as used
    cursor.execute("""
        UPDATE email_verification_codes SET used = 1 WHERE id = ?
    """, (code_id,))
    
    conn.commit()
    conn.close()
    
    return True, "Account created successfully! You can now login."


def resend_verification_code(email):
    """Resend verification code for pending signup"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get latest unused code
    cursor.execute("""
        SELECT user_data FROM email_verification_codes
        WHERE email = ? AND used = 0
        ORDER BY created_at DESC
        LIMIT 1
    """, (email,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return False, "No pending verification found. Please sign up again."
    
    user_data = json.loads(result[0])
    return send_verification_code(email, user_data)


# Initialize table on import
create_verification_table()