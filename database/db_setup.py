import sqlite3

def init_db():
    conn = sqlite3.connect("database/otakuzone.db")
    cursor = conn.cursor()

    # Create Users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT,
        birthdate TEXT,
        age INTEGER,
        address TEXT,
        gender TEXT,
        bio TEXT,
        role TEXT DEFAULT 'user'
    )''')

    # Create Anime table
    cursor.execute('''CREATE TABLE IF NOT EXISTS anime (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        genre TEXT,
        category TEXT,
        description TEXT,
        episodes INTEGER,
        image_path TEXT
    )''')

    # Create Favorites table
    cursor.execute('''CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        anime_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (anime_id) REFERENCES anime(id)
    )''')
    
    cursor.execute("INSERT INTO anime (title, genre, category, description, episodes, image_path) VALUES ('Bleach: Thousand-Year Blood War', 'Action, Supernatural', 'Ongoing', 'Bleach final arc', 2, '')")
    cursor.execute("INSERT INTO anime (title, genre, category, description, episodes, image_path) VALUES ('Naruto', 'Action, Adventure', 'Completed', 'Ninja story', 500, '')")

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully.")

if __name__ == "__main__":
    init_db()
