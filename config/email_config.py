import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Email Configuration
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Validate required variables
if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
    raise ValueError(
        "EMAIL_ADDRESS and EMAIL_PASSWORD must be set in .env file!\n"
        "Please copy .env.example to .env and fill in your credentials."
    )

# Email Templates
RESET_PASSWORD_SUBJECT = "OtakuZone - Password Reset Code"
RESET_PASSWORD_BODY = """
Hello,

You requested to reset your password for OtakuZone.

Your verification code is: {code}

This code will expire in 10 minutes.

If you didn't request this, please ignore this email.

Best regards,
OtakuZone Team
"""