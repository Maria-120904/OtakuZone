import sqlite3
from datetime import datetime, timedelta
from services.email_service import generate_reset_code, send_2fa_code_email

DB_PATH = "database/otakuzone.db"


def create_two_factor_table():
    """Create table to store 2FA codes"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS two_factor_codes (
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


def is_2fa_enabled(email):
    """Check if user has 2FA enabled"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT two_factor_enabled FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    return result and result[0] == 1


def toggle_2fa(user_id, enabled):
    """Enable or disable 2FA for user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users SET two_factor_enabled = ? WHERE id = ?
    """, (1 if enabled else 0, user_id))
    conn.commit()
    conn.close()


def send_2fa_code(email):
    """
    Generate and send 2FA code to user's email
    Returns: (success: bool, message: str)
    """
    print(f"\n2FA: Checking if 2FA enabled for: {email}")
    
    # Check if 2FA is enabled for this user
    if not is_2fa_enabled(email):
        print(f"2FA: Not enabled for: {email}")
        return True, "2FA not enabled"
    
    print(f"2FA: Enabled for: {email}")
    
    # Generate code
    code = generate_reset_code()
    print(f"2FA: Generated code: {code}")
    
    # Save to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Delete old unused codes for this email
    cursor.execute("""
        DELETE FROM two_factor_codes 
        WHERE email = ? AND used = 0
    """, (email,))
    print(f"2FA: Deleted old codes for: {email}")
    
    # Create new code
    created_at = datetime.now().isoformat()
    expires_at = (datetime.now() + timedelta(minutes=5)).isoformat()
    
    cursor.execute("""
        INSERT INTO two_factor_codes (email, code, created_at, expires_at)
        VALUES (?, ?, ?, ?)
    """, (email, code, created_at, expires_at))
    print(f"2FA: Saved code to database")
    
    conn.commit()
    conn.close()
    
    # Send email
    print(f"2FA: Attempting to send email...")
    success, error = send_2fa_code_email(email, code)
    
    if success:
        print(f"2FA: Email sent successfully!")
        return True, "2FA code sent to your email."
    else:
        print(f"2FA: Email failed: {error}")
        return False, f"Failed to send 2FA code: {error}"


def verify_2fa_code(email, code):
    """
    Verify if 2FA code is valid
    Returns: (valid: bool, message: str)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get the latest unused code for this email
    cursor.execute("""
        SELECT id, expires_at FROM two_factor_codes
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
    
    # Mark code as used
    cursor.execute("""
        UPDATE two_factor_codes SET used = 1 WHERE id = ?
    """, (code_id,))
    
    conn.commit()
    conn.close()
    
    return True, "2FA code verified successfully."


# Initialize table on import
create_two_factor_table()