import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database
DB_PATH = os.getenv("DB_PATH", "database/otakuzone.db")

# Application
APP_NAME = os.getenv("APP_NAME", "OtakuZone")
SECRET_KEY = os.getenv("SECRET_KEY")

# Directories
PROFILE_DIR = "assets/profile"
ANIME_IMG_DIR = "assets/anime"
VIDEOS_DIR = "assets/videos"

# Google OAuth (optional)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# Validate critical settings
if not SECRET_KEY:
    print("⚠️ WARNING: SECRET_KEY not set in .env file!")