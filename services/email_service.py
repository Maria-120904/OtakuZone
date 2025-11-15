import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# Import email configuration
try:
    from config.email_config import (
        EMAIL_HOST,
        EMAIL_PORT,
        EMAIL_ADDRESS,
        EMAIL_PASSWORD,
        RESET_PASSWORD_SUBJECT,
        RESET_PASSWORD_BODY
    )
    print(f"Email config loaded: {EMAIL_ADDRESS}")
except ImportError as e:
    print(f"Failed to import email config: {e}")
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_PORT = 587
    EMAIL_ADDRESS = "your_email@gmail.com"
    EMAIL_PASSWORD = "your_app_password"
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


def generate_reset_code():
    """Generate a 6-digit verification code"""
    return ''.join(random.choices(string.digits, k=6))


def send_reset_code_email(recipient_email, reset_code):
    """
    Send password reset code to user's email
    Returns: (success: bool, error_message: str or None)
    """
    print(f"\n{'='*60}")
    print(f"EMAIL SENDING DEBUG")
    print(f"{'='*60}")
    print(f"From: {EMAIL_ADDRESS}")
    print(f"To: {recipient_email}")
    print(f"Code: {reset_code}")
    print(f"SMTP Server: {EMAIL_HOST}:{EMAIL_PORT}")
    print(f"Password Length: {len(EMAIL_PASSWORD)} chars")
    print(f"{'='*60}\n")
    
    try:
        # Create message
        message = MIMEMultipart()
        message["From"] = EMAIL_ADDRESS
        message["To"] = recipient_email
        message["Subject"] = RESET_PASSWORD_SUBJECT
        
        # Email body
        body = RESET_PASSWORD_BODY.format(code=reset_code)
        message.attach(MIMEText(body, "plain"))
        
        print("Step 1: Connecting to SMTP server...")
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=30)
        print("Connected!")
        
        print("Step 2: Starting TLS encryption...")
        server.set_debuglevel(1)  # Show detailed SMTP communication
        server.starttls()
        print("TLS started!")
        
        print("Step 3: Logging in...")
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        print("Login successful!")
        
        print("Step 4: Sending email...")
        server.send_message(message)
        print("Email sent!")
        
        server.quit()
        print("\nEMAIL SENT SUCCESSFULLY!\n")
        return True, None
        
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"Authentication failed: {str(e)}"
        print(error_msg)
        return False, "Authentication failed. Check your email password."
        
    except smtplib.SMTPConnectError as e:
        error_msg = f"Connection failed: {str(e)}"
        print(error_msg)
        return False, "Cannot connect to email server."
        
    except smtplib.SMTPServerDisconnected as e:
        error_msg = f"Server disconnected: {str(e)}"
        print(error_msg)
        return False, "Email server disconnected."
        
    except Exception as e:
        error_msg = f"Error: {type(e).__name__}: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return False, f"Error: {str(e)}"


def send_test_email():
    """Test email sending (for debugging)"""
    test_code = generate_reset_code()
    print(f"\n{'='*60}")
    print(f"TESTING EMAIL SERVICE")
    print(f"{'='*60}")
    
    success, error = send_reset_code_email(EMAIL_ADDRESS, test_code)
    
    if success:
        print(f"\nTest email sent successfully!")
        print(f"Check inbox: {EMAIL_ADDRESS}")
        print(f"Reset code: {test_code}")
    else:
        print(f"\nFailed to send email")
        print(f"Error: {error}")
    
    print(f"{'='*60}\n")
    return success