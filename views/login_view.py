import flet as ft
import sqlite3
import bcrypt
import re
import threading
import asyncio
from services.session_manager import SessionManager
from services.login_security import (
    record_login_attempt,
    is_account_locked,
    clear_login_attempts,
    get_failed_attempts,
    get_lockout_time_remaining
)
from services.google_auth import get_google_user_info
from services.google_user_service import get_or_create_google_user
from services.two_factor_service import is_2fa_enabled, send_2fa_code
from theme import set_theme, primary_button, input_field

DB_PATH = "database/otakuzone.db"

# Get user by email
def get_user_by_email(email):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, username, email, password, role FROM users WHERE email = ?",
        (email,),
    )
    user = cursor.fetchone()
    conn.close()
    return user

# Main login view
def main(page: ft.Page):
    set_theme(page)
    page.title = "OtakuZone - Login"

    session = SessionManager(page)

    # UI Components
    email_input = input_field("Email")
    password_input = input_field("Password", password=True)
    message_text = ft.Text(value="", color="red", size=14)
    
    # Create buttons that can be disabled
    signin_button = ft.ElevatedButton(
        text="Sign In",
        width=300,
        height=45,
        bgcolor="#E50914",
        color="white",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            overlay_color="#ff4040",
        ),
        on_click=None
    )
    
    # Forgot Password Button
    forgot_password_button = ft.TextButton(
        "Forgot Password?",
        style=ft.ButtonStyle(color="#E50914"),
        on_click=None
    )
    
    # Google Sign In Button
    google_button = ft.ElevatedButton(
        content=ft.Row(
            [
                ft.Image(
                    src="https://www.google.com/favicon.ico",
                    width=20,
                    height=20,
                ),
                ft.Text("Continue with Google", size=14, color="black"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        ),
        width=300,
        height=45,
        bgcolor="white",
        color="white",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
        on_click=None
    )
    
    signup_link = ft.TextButton(
        "Don't have an account? Sign up",
        style=ft.ButtonStyle(color="#E50914"),
        on_click=None
    )
    
    # Forgot Password Handler
    def handle_forgot_password(e):
        page.go("/forgot-password")
    
    # Google Sign In Handler
    def handle_google_signin():
        message_text.value = "Opening Google Sign-In..."
        message_text.color = "blue"
        google_button.disabled = True
        signin_button.disabled = True
        page.update()
        
        def google_auth_thread():
            user_info, error = get_google_user_info()
            
            if error:
                message_text.value = f"Error: {error}"
                message_text.color = "red"
                google_button.disabled = False
                signin_button.disabled = False
                page.update()
                return
            
            if user_info:
                # Get or create user
                user_id, role, is_new = get_or_create_google_user(
                    user_info['email'],
                    user_info['name'],
                    user_info['google_id']
                )
                
                if user_id is None:
                    message_text.value = "Email registered with password. Please use email/password login."
                    message_text.color = "red"
                    google_button.disabled = False
                    signin_button.disabled = False
                    page.update()
                    return
                
                # Login successful
                session.login(user_id, role, user_info['email'])
                message_text.value = f"Welcome {user_info['name']}!"
                message_text.color = "green"
                page.update()
                
                # NEW: Resize window based on role
                import time
                time.sleep(1)
                if role == "admin":
                    page.window_maximized = True
                    page.window_resizable = True
                    page.update()
                    page.go("/admin")
                else:
                    page.go("/home")
        
        threading.Thread(target=google_auth_thread, daemon=True).start()
    
    # NEW: Lockout timer in alert dialog
    def start_lockout_timer(email, total_seconds):
        # Disable all inputs and buttons
        signin_button.disabled = True
        google_button.disabled = True
        signup_link.disabled = True
        email_input.disabled = True
        password_input.disabled = True
        forgot_password_button.disabled = True
        page.update()
        
        # Create dialog components
        timer_display = ft.Text(
            value="",
            size=18,
            weight="bold",
            color="#E50914",
            text_align="center"
        )
        
        status_message = ft.Text(
            value="Account locked. Please wait...",
            size=14,
            color="red",
            text_align="center"
        )
        
        cancel_button = ft.ElevatedButton(
            "OK",
            bgcolor=ft.Colors.GREY_100,
            color="black", 
            disabled=True, 
            on_click=None
        )
        
        def close_dialog(e):
            lockout_dialog.open = False
            page.update()
        
        cancel_button.on_click = close_dialog
        
        # Create the alert dialog
        lockout_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                [
                    ft.Text("Account Locked", size=20, weight="bold", color="E50914"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        status_message,
                        ft.Divider(height=5, color="transparent"),
                        timer_display,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=3,
                ),
                width=220,
                height=90,
                padding=15,
            ),
            actions=[
                cancel_button,
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        # Show dialog
        page.overlay.append(lockout_dialog)
        lockout_dialog.open = True
        page.update()
        
        # Countdown async function
        async def countdown():
            while True:
                remaining = get_lockout_time_remaining(email, lockout_minutes=2)
                
                if remaining > 0:
                    minutes = remaining // 60
                    seconds = remaining % 60
                    timer_display.value = f"Locked for: {minutes}m {seconds}s"
                    status_message.value = "Account locked. Please wait..."
                    status_message.color = "red"
                    page.update()
                    
                    await asyncio.sleep(1)
                else:
                    # Timer finished - enable everything
                    timer_display.value = "Time's up!"
                    status_message.value = "You can try logging in again."
                    status_message.color = "green"
                    cancel_button.disabled = False
                    
                    # Change button color to red when enabled
                    cancel_button.bgcolor = "#E50914"
                    cancel_button.color = "white"
                    
                    # Re-enable inputs and buttons
                    signin_button.disabled = False
                    google_button.disabled = False
                    signup_link.disabled = False
                    email_input.disabled = False
                    password_input.disabled = False
                    forgot_password_button.disabled = False
                    
                    page.update()
                    break
        
        page.run_task(countdown)

    # Handle login logic
    def handle_login(e):
        email = email_input.value.strip()
        password = password_input.value.strip()

        # Validation
        if not email or not password:
            message_text.value = "Please fill in all fields."
            message_text.color = "red"
            page.update()
            return

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            message_text.value = "Invalid email format."
            message_text.color = "red"
            page.update()
            return

        # Check if account is locked
        if is_account_locked(email, max_attempts=5):
            remaining_seconds = get_lockout_time_remaining(email, lockout_minutes=2)
            if remaining_seconds > 0:
                start_lockout_timer(email, remaining_seconds)
                return

        user = get_user_by_email(email)
        if user:
            stored_hash = user[4]

            # Check hashed password
            if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
                clear_login_attempts(email)
                record_login_attempt(email, success=True)
                
                # Check if 2FA is enabled
                if is_2fa_enabled(email):
                    # Send 2FA code
                    message_text.value = "Sending 2FA code..."
                    message_text.color = "blue"
                    page.update()
                    
                    success, msg = send_2fa_code(email)
                    
                    if success:
                        # Store user data in page session for 2FA view
                        page.session.set("2fa_user_data", {
                            'user_id': user[0],
                            'role': user[5],
                            'email': user[3]
                        })
                        page.go("/2fa-verify")
                    else:
                        message_text.value = f"Failed to send 2FA code: {msg}"
                        message_text.color = "red"
                        page.update()
                else:
                    # NEW: No 2FA - direct login with window resize
                    session.login(user[0], user[5], user[3])
                    
                    if user[5] == "admin":
                        # Maximize window for admin
                        page.window_maximized = True
                        page.window_resizable = True
                        page.update()
                        page.go("/admin")
                    else:
                        # Regular user stays at mobile size
                        page.go("/home")
            else:
                # Record failed attempt
                record_login_attempt(email, success=False)
                new_failed_count = get_failed_attempts(email, minutes=2)
                remaining = 5 - new_failed_count
                
                if remaining > 0:
                    message_text.value = f"Incorrect password. {remaining} attempt(s) remaining."
                    message_text.color = "orange"
                else:
                    # Account locked - show dialog
                    message_text.value = ""
                    page.update()
                    start_lockout_timer(email, 120)
        else:
            # Record failed attempt
            record_login_attempt(email, success=False)
            new_failed_count = get_failed_attempts(email, minutes=2)
            remaining = 5 - new_failed_count
            
            if remaining > 0:
                message_text.value = f"Invalid credentials. {remaining} attempt(s) remaining."
                message_text.color = "orange"
            else:
                # Account locked - show dialog
                message_text.value = ""
                page.update()
                start_lockout_timer(email, 120)

        page.update()
    
    # Assign click handlers
    signin_button.on_click = handle_login
    google_button.on_click = lambda e: handle_google_signin()
    forgot_password_button.on_click = handle_forgot_password
    
    def go_to_signup(e):
        page.go("/signup")
    
    signup_link.on_click = go_to_signup

    # Check lockout when email loses focus
    def on_email_blur(e):
        email = email_input.value.strip()
        if email and is_account_locked(email, max_attempts=5):
            remaining = get_lockout_time_remaining(email, lockout_minutes=2)
            if remaining > 0:
                start_lockout_timer(email, remaining)
    
    email_input.on_blur = on_email_blur

    # Logo and brand image
    logo_image = ft.Image(
        src="assets/logo/logo.png",
        width=120,
        height=120,
        fit=ft.ImageFit.CONTAIN,
    )

    # Sign In button + Forgot Password aligned
    signin_and_forgot_container = ft.Column(
        [
            signin_button,
            ft.Container(
                content=forgot_password_button,
                width=300,
                alignment=ft.alignment.center_right,
                padding=ft.padding.only(top=0),
            ),
        ],
        spacing=0,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
    )

    layout = ft.Column(
        [
            # Logo at the top
            ft.Container(
                content=logo_image,
                alignment=ft.alignment.center,
            ),
            ft.Container(
                ft.Text("Welcome back!", size=20, weight="bold", color="white"),
                alignment=ft.alignment.center
            ),
            ft.Text(
                "Use your email and password to log in",
                size=12,
                color="#b3b3b3",
            ),
            ft.Divider(height=10, color="transparent"),
            email_input,
            password_input,
            signin_and_forgot_container,
            ft.Text("or", color="#b3b3b3"),
            google_button,
            signup_link,
            ft.Container(height=4),
            message_text
        ],
        alignment="center",
        horizontal_alignment="center",
        spacing=10,
    )
    
    page.add(layout)
    
if __name__ == "__main__":
    ft.app(target=main)