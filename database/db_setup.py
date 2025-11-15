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
    two_factor_enabled INTEGER DEFAULT 0
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS anime (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    genre TEXT,
    category TEXT,
    description TEXT,
    episodes INTEGER,
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

# Two-Factor Authentication codes table
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

# INSERT SAMPLE USERS
def insert_user(name, username, email, password, role="user"):
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    cursor.execute("""
        INSERT OR IGNORE INTO users (name, username, email, password, role, two_factor_enabled)
        VALUES (?, ?, ?, ?, ?, 0)
    """, (name, username, email, hashed_pw, role))

# Admin account
insert_user("Admin", "admin", "admin@otakuzone.com", "admin123", "admin")

# Regular user account
insert_user("Test User", "testuser", "user@otakuzone.com", "user123", "user")

# INSERT SAMPLE ANIME
anime_samples = [
    ("Bleach: Thousand-Year Blood War", "Action, Supernatural", "Ongoing", "Ichigo Kurosaki faces Quincy invasion.", 13, ""),
    ("Naruto Shippuden", "Action, Adventure", "Completed", "Naruto's journey to become Hokage.", 500, ""),
    ("Attack on Titan", "Action, Drama", "Completed", "Eren Yeager fights for freedom against Titans.", 75, ""),
    ("Demon Slayer", "Action, Fantasy", "Ongoing", "Tanjiro seeks revenge for his family.", 40, ""),
    ("One Piece", "Adventure, Comedy", "Ongoing", "Luffy and his crew search for the One Piece.", 1000, ""),
    ("Jujutsu Kaisen", "Action, Supernatural", "Ongoing", "Yuji Itadori becomes host to Sukuna.", 48, ""),
    ("Tokyo Ghoul", "Horror, Thriller", "Completed", "Kaneki becomes half-ghoul after an encounter.", 48, "")
]

cursor.executemany("""
INSERT OR IGNORE INTO anime (title, genre, category, description, episodes, image_path)
VALUES (?, ?, ?, ?, ?, ?)
""", anime_samples)

conn.commit()
conn.close()

print("Database setup complete - tables created and sample data added!")
print("Security tables (login_attempts, password_reset_codes, two_factor_codes) initialized!")
print("Google ID column added to users table!")
print("Two-Factor Authentication column added to users table!")