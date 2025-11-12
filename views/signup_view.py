import flet as ft
import sqlite3
import bcrypt
import re
import threading
from theme import set_theme, primary_button, input_field
from services.google_auth import get_google_user_info
from services.google_user_service import get_or_create_google_user

DB_PATH = "database/otakuzone.db"


# --- Database Helpers ---
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
            role TEXT DEFAULT 'user'
        )
    """)
    conn.commit()
    conn.close()


def add_user(name, username, email, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check for existing email or username
    cursor.execute("SELECT id FROM users WHERE email=? OR username=?", (email, username))
    if cursor.fetchone():
        conn.close()
        raise ValueError("Email or username already exists.")

    # Hash password
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    cursor.execute(
        "INSERT INTO users (name, username, email, password) VALUES (?, ?, ?, ?)",
        (name, username, email, hashed_pw),
    )
    conn.commit()
    conn.close()


# --- Main Page ---
def main(page: ft.Page):
    set_theme(page)
    page.title = "OtakuZone - Sign Up"
    page.scroll = "auto"

    create_user_table()

    # Input fields
    name_input = input_field("Full Name")
    username_input = input_field("Username")
    email_input = input_field("Email")
    password_input = input_field("Password", password=True)
    message_text = ft.Text(value="", color="red", size=14)

    # ✅ Google Sign Up Button
    google_button = ft.ElevatedButton(
        content=ft.Row(
            [
                ft.Image(
                    src="https://www.google.com/favicon.ico",
                    width=20,
                    height=20,
                ),
                ft.Text("Continue with Google", size=14, color="white"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        ),
        width=300,
        height=45,
        bgcolor="#4285F4",
        color="white",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
        on_click=lambda e: handle_google_signup(),
    )

    # ✅ Google Sign Up Handler (Real Implementation)
    def handle_google_signup():
        message_text.value = "🔄 Opening Google Sign-In..."
        message_text.color = "blue"
        google_button.disabled = True
        page.update()
        
        def google_auth_thread():
            user_info, error = get_google_user_info()
            
            if error:
                message_text.value = f"❌ Error: {error}"
                message_text.color = "red"
                google_button.disabled = False
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
                    message_text.value = "❌ Email already registered with password login. Please use regular login."
                    message_text.color = "red"
                    google_button.disabled = False
                    page.update()
                    return
                
                if is_new:
                    message_text.value = f"✅ Account created for {user_info['email']}! Redirecting to login..."
                    message_text.color = "green"
                    page.update()
                    import time
                    time.sleep(2)
                    page.go("/login")
                else:
                    message_text.value = "ℹ️ Account already exists. Please use login page."
                    message_text.color = "orange"
                    google_button.disabled = False
                    page.update()
        
        # Run in separate thread to avoid blocking UI
        threading.Thread(target=google_auth_thread, daemon=True).start()

    # --- Signup handler ---
    def handle_signup(e):
        name = name_input.value.strip()
        username = username_input.value.strip()
        email = email_input.value.strip()
        password = password_input.value.strip()

        # Validation
        if not all([name, username, email, password]):
            message_text.value = "⚠ Please fill in all fields."
            message_text.color = "red"
            page.update()
            return

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            message_text.value = "⚠ Invalid email format."
            message_text.color = "red"
            page.update()
            return

        if len(password) < 6:
            message_text.value = "⚠ Password must be at least 6 characters long."
            message_text.color = "red"
            page.update()
            return

        try:
            add_user(name, username, email, password)
            message_text.value = "✅ Account created successfully! Redirecting..."
            message_text.color = "green"
            page.update()
            page.go("/login")
        except ValueError as ve:
            message_text.value = str(ve)
            message_text.color = "red"
        except Exception as ex:
            message_text.value = f"Error: {str(ex)}"
            message_text.color = "red"

        page.update()

    # --- Navigation ---
    def go_to_login(e):
        page.go("/login")

    # --- Layout ---
    layout = ft.Column(
        [
            ft.Container(
                ft.Text("Create New Account", size=26, weight="bold", color="white"),
                alignment=ft.alignment.center,
                padding=10
            ),
            ft.Text("Already registered? Log in here.", size=14, color="#b3b3b3"),
            ft.Divider(height=20, color="transparent"),
            name_input,
            username_input,
            email_input,
            password_input,
            primary_button("Sign Up", on_click=handle_signup),
            ft.Container(height=10),
            ft.Text("or", color="#b3b3b3"),
            ft.Container(height=5),
            google_button,
            ft.Container(height=15),
            ft.TextButton(
                "Already have an account? Login",
                on_click=go_to_login,
                style=ft.ButtonStyle(color="#E50914"),
            ),
            ft.Container(height=10),
            message_text,
        ],
        alignment="center",
        horizontal_alignment="center",
        spacing=10,
    )

    page.add(layout)


if __name__ == "__main__":
    ft.app(target=main)