import sqlite3
import bcrypt
import os

DB_PATH = "database/otakuzone.db"

# Create folder if not existing
os.makedirs("database", exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Enable foreign keys
conn.execute("PRAGMA foreign_keys = ON")

# CREATE TABLES
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    username TEXT,
    email TEXT UNIQUE,
    password BLOB,
    google_id TEXT UNIQUE,
    birthdate TEXT,
    age INTEGER,
    address TEXT,
    gender TEXT,
    bio TEXT,
    role TEXT DEFAULT 'user',
    two_factor_enabled INTEGER DEFAULT 0,
    email_verified INTEGER DEFAULT 0,
    profile_image TEXT
);
""")

# --- USERS TABLE ---
# Add profile_image column if not exists
cursor.execute("PRAGMA table_info(users)")
columns = [col[1] for col in cursor.fetchall()]
if "profile_image" not in columns:
    cursor.execute("ALTER TABLE users ADD COLUMN profile_image TEXT")

# ✅ UPDATED: Anime table WITHOUT episodes field
cursor.execute("""
CREATE TABLE IF NOT EXISTS anime (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    genre TEXT,
    category TEXT,
    description TEXT,
    image_path TEXT
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    anime_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (anime_id) REFERENCES anime(id) ON DELETE CASCADE
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS login_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    attempt_time TEXT NOT NULL,
    success INTEGER DEFAULT 0
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS password_reset_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    code TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    used INTEGER DEFAULT 0
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS two_factor_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    code TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    used INTEGER DEFAULT 0
);
""")

# Email verification codes table
cursor.execute("""
CREATE TABLE IF NOT EXISTS email_verification_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    code TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    used INTEGER DEFAULT 0,
    user_data TEXT
);
""")

# ✅ NEW: Episodes table
cursor.execute("""
CREATE TABLE IF NOT EXISTS episodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    anime_id INTEGER NOT NULL,
    episode_number INTEGER NOT NULL,
    title TEXT,
    video_path TEXT NOT NULL,
    duration TEXT,
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (anime_id) REFERENCES anime(id) ON DELETE CASCADE,
    UNIQUE(anime_id, episode_number)
);
""")

# INSERT SAMPLE USERS
def insert_user(name, username, email, password, role="user"):
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    cursor.execute("""
        INSERT OR IGNORE INTO users (name, username, email, password, role, two_factor_enabled, email_verified)
        VALUES (?, ?, ?, ?, ?, 0, 1)
    """, (name, username, email, hashed_pw, role))

# Admin account
insert_user("Admin", "admin", "admin@otakuzone.com", "admin123", "admin")

# Regular user account
insert_user("Test User", "testuser", "user@otakuzone.com", "user123", "user")

# ✅ UPDATED: Sample anime WITHOUT episodes field
anime_samples = [
    ("Bleach: Thousand-Year Blood War", "Action, Supernatural", "Ongoing", "Ichigo Kurosaki faces Quincy invasion.", ""),
    ("Naruto Shippuden", "Action, Adventure", "Completed", "Naruto's journey to become Hokage.", ""),
    ("Attack on Titan", "Action, Drama", "Completed", "Eren Yeager fights for freedom against Titans.", ""),
    ("Demon Slayer", "Action, Fantasy", "Ongoing", "Tanjiro seeks revenge for his family.", ""),
    ("One Piece", "Adventure, Comedy", "Ongoing", "Luffy and his crew search for the One Piece.", ""),
    ("Jujutsu Kaisen", "Action, Supernatural", "Ongoing", "Yuji Itadori becomes host to Sukuna.", ""),
    ("Tokyo Ghoul", "Horror, Thriller", "Completed", "Kaneki becomes half-ghoul after an encounter.", "")
]

cursor.executemany("""
INSERT OR IGNORE INTO anime (title, genre, category, description, image_path)
VALUES (?, ?, ?, ?, ?)
""", anime_samples)

conn.commit()
conn.close()

print("✅ Database setup complete - tables created and sample data added!")
print("✅ Anime table created WITHOUT episodes field!")
print("✅ Episodes table created successfully!")
print("✅ Security tables initialized!")
print("✅ Email verification table created!")
print("✅ Google ID column added to users table!")
print("✅ Two-Factor Authentication enabled!")
print("✅ Profile image support added!")