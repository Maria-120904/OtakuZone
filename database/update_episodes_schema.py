import sqlite3
import os

DB_PATH = "database/otakuzone.db"

def update_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Create episodes table
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
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Episodes table created successfully!")

if __name__ == "__main__":
    update_schema()