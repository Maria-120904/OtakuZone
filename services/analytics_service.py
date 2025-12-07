import sqlite3
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "database/otakuzone.db")


# USER ANALYTICS
def get_total_users():
    """Get total registered users"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'user'")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_admin_count():
    """Get total admins"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_verified_users():
    """Get email verified users"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE email_verified = 1")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_google_users():
    """Get users registered via Google"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE google_id IS NOT NULL")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_users_by_gender():
    """Get users grouped by gender"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            COALESCE(gender, 'Not Specified') as gender,
            COUNT(*) as count
        FROM users 
        WHERE role = 'user'
        GROUP BY gender
    """)
    data = cursor.fetchall()
    conn.close()
    return data

# ANIME ANALYTICS
def get_total_anime():
    """Get total anime"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM anime")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_total_episodes():
    """Get total episodes"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM episodes")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_anime_by_category():
    """Get anime grouped by category"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            category,
            COUNT(*) as count
        FROM anime
        GROUP BY category
    """)
    data = cursor.fetchall()
    conn.close()
    return data

def get_top_genres():
    """Get top 5 genres by count"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT genre, COUNT(*) as count
        FROM anime
        GROUP BY genre
        ORDER BY count DESC
        LIMIT 5
    """)
    data = cursor.fetchall()
    conn.close()
    return data

def get_anime_with_most_episodes():
    """Get top 5 anime with most episodes"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            a.title,
            COUNT(e.id) as episode_count
        FROM anime a
        LEFT JOIN episodes e ON a.id = e.anime_id
        GROUP BY a.id
        ORDER BY episode_count DESC
        LIMIT 5
    """)
    data = cursor.fetchall()
    conn.close()
    return data


# FAVORITES ANALYTICS
def get_total_favorites():
    """Get total favorites"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM favorites")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_most_favorited_anime():
    """Get top 5 most favorited anime"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            a.title,
            COUNT(f.id) as favorite_count
        FROM anime a
        LEFT JOIN favorites f ON a.id = f.anime_id
        GROUP BY a.id
        ORDER BY favorite_count DESC
        LIMIT 5
    """)
    data = cursor.fetchall()
    conn.close()
    return data

# GROWTH ANALYTICS
def get_user_growth_last_7_days():
    """Get user registrations for last 7 days (simulated)"""
    # Note: This assumes you add a created_at column to users table
    # For now, we'll return sample data
    from datetime import datetime, timedelta
    
    data = []
    for i in range(7, 0, -1):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        # Simulated count - in production, query actual data
        data.append((date, 5 + (i % 3) * 2))
    
    return data

def get_favorites_growth_last_7_days():
    """Get favorites added for last 7 days (simulated)"""
    from datetime import datetime, timedelta
    
    data = []
    for i in range(7, 0, -1):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        data.append((date, 8 + (i % 4) * 3))
    
    return data

# INSIGHTS
def get_platform_insights():
    """Generate platform insights"""
    total_users = get_total_users()
    verified = get_verified_users()
    google_users = get_google_users()
    total_anime = get_total_anime()
    total_episodes = get_total_episodes()
    total_favorites = get_total_favorites()
    
    insights = []
    
    # User verification rate
    if total_users > 0:
        verification_rate = (verified / total_users) * 100
        if verification_rate < 50:
            insights.append(f"⚠️ Only {verification_rate:.1f}% users verified their email")
        else:
            insights.append(f"✅ {verification_rate:.1f}% email verification rate")
    
    # Google OAuth adoption
    if total_users > 0:
        google_rate = (google_users / total_users) * 100
        insights.append(f"📱 {google_rate:.1f}% users login via Google")
    
    # Content ratio
    if total_anime > 0:
        avg_episodes = total_episodes / total_anime
        insights.append(f"📺 Average {avg_episodes:.1f} episodes per anime")
    
    # Engagement
    if total_anime > 0 and total_favorites > 0:
        avg_favorites = total_favorites / total_anime
        insights.append(f"❤️ Average {avg_favorites:.1f} favorites per anime")
    
    # Platform health
    if total_users > 100:
        insights.append("🚀 Platform growing steadily!")
    elif total_users > 50:
        insights.append("📈 Good user growth")
    else:
        insights.append("🌱 Early stage - keep growing!")
    
    return insights