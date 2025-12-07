import flet as ft
import sqlite3
import bcrypt
import re
import threading
from theme import set_theme, primary_button, input_field
from services.google_auth import get_google_user_info
from services.google_user_service import get_or_create_google_user
from services.email_verification_service import send_verification_code

DB_PATH = "database/otakuzone.db"


# Database Helpers
def create_user_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            username TEXT UNIQUE,
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
            email_verified INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


# Main Page
def main(page: ft.Page):
    set_theme(page)
    page.title = "OtakuZone - Sign Up"
    page.scroll = "auto"

    create_user_table()

    # ✅ Input fields - same width as login (300px)
    name_input = input_field("Full Name")
    username_input = input_field("Username")
    email_input = input_field("Email")
    password_input = input_field("Password", password=True)
    message_text = ft.Text(value="", color="red", size=14)

    # ✅ Sign Up Button
    signup_button = ft.ElevatedButton(
        text="Sign Up",
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

    # ✅ Google Sign Up Button - same as login (white bg, black text)
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

    # ✅ Already have account link
    login_link = ft.TextButton(
        "Already have an account? Login",
        style=ft.ButtonStyle(color="#E50914"),
        on_click=None
    )

    # Google Sign Up Handler
    def handle_google_signup():
        message_text.value = "Opening Google Sign-In..."
        message_text.color = "blue"
        google_button.disabled = True
        signup_button.disabled = True
        page.update()
        
        def google_auth_thread():
            user_info, error = get_google_user_info()
            
            if error:
                message_text.value = f"Error: {error}"
                message_text.color = "red"
                google_button.disabled = False
                signup_button.disabled = False
                page.update()
                return
            
            if user_info:
                # Create or get user
                user_id, role, is_new = get_or_create_google_user(
                    user_info['email'],
                    user_info['name'],
                    user_info['google_id']
                )
                
                if user_id is None:
                    message_text.value = "Email already registered with password login. Please use regular login."
                    message_text.color = "red"
                    google_button.disabled = False
                    signup_button.disabled = False
                    page.update()
                    return
                
                if is_new:
                    message_text.value = f"Account created for {user_info['email']}! Redirecting to login..."
                    message_text.color = "green"
                    page.update()
                    import time
                    time.sleep(2)
                    page.go("/login")
                else:
                    message_text.value = "Account already exists. Please use login page."
                    message_text.color = "orange"
                    google_button.disabled = False
                    signup_button.disabled = False
                    page.update()
        
        threading.Thread(target=google_auth_thread, daemon=True).start()

    # Signup handler
    def handle_signup(e):
        name = name_input.value.strip()
        username = username_input.value.strip()
        email = email_input.value.strip()
        password = password_input.value.strip()

        # Validation
        if not all([name, username, email, password]):
            message_text.value = "Please fill in all fields."
            message_text.color = "red"
            page.update()
            return

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            message_text.value = "Invalid email format."
            message_text.color = "red"
            page.update()
            return

        if len(password) < 6:
            message_text.value = "Password must be at least 6 characters long."
            message_text.color = "red"
            page.update()
            return

        # Prepare user data
        user_data = {
            'name': name,
            'username': username,
            'password': password
        }

        # Send verification code
        message_text.value = "Sending verification code to your email..."
        message_text.color = "blue"
        page.update()

        success, msg = send_verification_code(email, user_data)

        if success:
            message_text.value = "Verification code sent! Redirecting..."
            message_text.color = "green"
            page.update()

            # Store email and name in session for verification page
            page.session.set("verification_email", email)
            page.session.set("verification_name", name)

            import time
            time.sleep(1)
            page.go("/verify-email")
        else:
            message_text.value = msg
            message_text.color = "red"
            page.update()

    # Navigation
    def go_to_login(e):
        page.go("/login")

    # Assign click handlers
    signup_button.on_click = handle_signup
    google_button.on_click = lambda e: handle_google_signup()
    login_link.on_click = go_to_login

    # ✅ Logo image (same as login)
    logo_image = ft.Image(
        src="assets/logo/logo.png",
        width=120,
        height=120,
        fit=ft.ImageFit.CONTAIN,
    )

    # ✅ Layout - matching login page structure
    layout = ft.Column(
        [
            # ✅ Logo at the top
            ft.Container(
                content=logo_image,
                alignment=ft.alignment.center,
            ),
            # ✅ Title - same size as login (20)
            ft.Container(
                ft.Text("Create New Account", size=20, weight="bold", color="white"),
                alignment=ft.alignment.center,
            ),
            # ✅ Subtitle - same size as login (12)
            ft.Text(
                "Sign up now and dive into endless anime adventures!",
                size=12,
                color="#b3b3b3",
            ),
            ft.Divider(height=10, color="transparent"),
            # ✅ Input fields (all 300px width)
            name_input,
            username_input,
            email_input,
            password_input,
            # ✅ Sign Up button (no extra buttons below - clean)
            signup_button,
            # ✅ "or" text
            ft.Text("or", color="#b3b3b3"),
            ft.Container(height=10),
            # ✅ Google button
            google_button,
            # ✅ Already have account link
            login_link,
            ft.Container(height=4),
            # ✅ Message text at bottom
            message_text,
        ],
        alignment="center",
        horizontal_alignment="center",
        spacing=10,
    )

    page.add(layout)


if __name__ == "__main__":
    ft.app(target=main)