import sqlite3
from datetime import datetime, timedelta

DB_PATH = "database/otakuzone.db"

def create_login_attempts_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            attempt_time TEXT NOT NULL,
            success INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def record_login_attempt(email, success=False):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # ✅ Store timestamp as ISO string
    attempt_time = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO login_attempts (email, attempt_time, success) VALUES (?, ?, ?)",
        (email, attempt_time, 1 if success else 0)
    )
    conn.commit()
    conn.close()

def get_failed_attempts(email, minutes=2):
    """Get failed login attempts in the last X minutes"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # ✅ Calculate cutoff time
    time_threshold = (datetime.now() - timedelta(minutes=minutes)).isoformat()
    
    cursor.execute("""
        SELECT COUNT(*) FROM login_attempts
        WHERE email = ? AND success = 0 AND attempt_time > ?
    """, (email, time_threshold))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_last_failed_attempt_time(email):
    """Get the timestamp of the most recent failed attempt"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT attempt_time FROM login_attempts
        WHERE email = ? AND success = 0
        ORDER BY attempt_time DESC
        LIMIT 1
    """, (email,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_lockout_time_remaining(email, lockout_minutes=2):
    """Calculate remaining lockout time in seconds"""
    last_attempt = get_last_failed_attempt_time(email)
    if not last_attempt:
        return 0
    
    last_attempt_dt = datetime.fromisoformat(last_attempt)
    lockout_end = last_attempt_dt + timedelta(minutes=lockout_minutes)
    now = datetime.now()
    
    if now < lockout_end:
        remaining = (lockout_end - now).total_seconds()
        return int(remaining)
    return 0

def clear_login_attempts(email):
    """Clear login attempts after successful login"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM login_attempts WHERE email = ?", (email,))
    conn.commit()
    conn.close()

def is_account_locked(email, max_attempts=5):
    """Check if account is locked due to too many failed attempts"""
    failed_count = get_failed_attempts(email, minutes=2)
    return failed_count >= max_attempts

# Initialize table on import
create_login_attempts_table()