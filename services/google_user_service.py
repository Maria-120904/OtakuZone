import sqlite3
import bcrypt

DB_PATH = "database/otakuzone.db"


def get_or_create_google_user(email, name, google_id):
    """
    Check if user exists with Google ID, if not create new user
    Returns: (user_id, role, is_new_user)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if user exists with this google_id
    cursor.execute("SELECT id, role FROM users WHERE google_id = ?", (google_id,))
    user = cursor.fetchone()
    
    if user:
        conn.close()
        return user[0], user[1], False  # Existing user
    
    # Check if email already exists (linked to different account)
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    existing_email = cursor.fetchone()
    
    if existing_email:
        conn.close()
        return None, None, None  # Email exists with different login method
    
    # Create new user with Google authentication
    # Generate username from email
    username = email.split('@')[0] + "_google"
    
    # No password needed for Google users (set to NULL or random hash)
    cursor.execute("""
        INSERT INTO users (name, username, email, google_id, role)
        VALUES (?, ?, ?, ?, 'user')
    """, (name, username, email, google_id))
    
    conn.commit()
    new_user_id = cursor.lastrowid
    conn.close()
    
    return new_user_id, 'user', True  # New user created


def link_google_to_existing_user(user_id, google_id):
    """Link Google ID to existing user account"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET google_id = ? WHERE id = ?", (google_id, user_id))
    conn.commit()
    conn.close()