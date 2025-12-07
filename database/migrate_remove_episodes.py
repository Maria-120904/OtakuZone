import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "database/otakuzone.db")

def migrate():
    """Migrate existing database to remove episodes column"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if episodes column exists
    cursor.execute("PRAGMA table_info(anime)")
    columns = {col[1]: col for col in cursor.fetchall()}
    
    if "episodes" in columns:
        print("⚠️  Found 'episodes' column in anime table. Migrating...")
        
        # Create new anime table without episodes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS anime_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                genre TEXT,
                category TEXT,
                description TEXT,
                image_path TEXT
            )
        """)
        
        # Copy data (excluding episodes column)
        cursor.execute("""
            INSERT INTO anime_new (id, title, genre, category, description, image_path)
            SELECT id, title, genre, category, description, image_path
            FROM anime
        """)
        
        # Drop old table and rename new one
        cursor.execute("DROP TABLE anime")
        cursor.execute("ALTER TABLE anime_new RENAME TO anime")
        
        print("✅ Migration complete! 'episodes' column removed.")
    else:
        print("✅ Database already up to date (no 'episodes' column found).")
    
    # Ensure episodes table exists
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
    print("✅ Episodes table ready!")

if __name__ == "__main__":
    migrate()