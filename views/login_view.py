import flet as ft
import sqlite3
import bcrypt
import re
from services.session_manager import SessionManager
from theme import set_theme, primary_button, input_field


# Get user by email
def get_user_by_email(email):
    conn = sqlite3.connect("database/otakuzone.db")
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

    # Handle login logic
    def handle_login(e):
        email = email_input.value.strip()
        password = password_input.value.strip()

        # Validation
        if not email or not password:
            message_text.value = "⚠ Please fill in all fields."
            page.update()
            return

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            message_text.value = "⚠ Invalid email format."
            page.update()
            return

        user = get_user_by_email(email)
        if user:
            stored_hash = user[4]

            # Check hashed password
            if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
                session.login(user[0], user[5], user[3])  # store session data

                # Redirect based on role
                if user[5] == "admin":
                    page.go("/admin/anime")
                else:
                    page.go("/home")
            else:
                message_text.value = "❌ Incorrect password."
        else:
            message_text.value = "❌ User not found."

        page.update()
        
    def go_to_signup(e):
        page.go("/signup")

    layout = ft.Column(
        [
            ft.Container(
                ft.Text("Welcome back!", size=26, weight="bold", color="white"),
                alignment=ft.alignment.center,
                padding=10,
            ),
            ft.Text(
                "Use your email and password to log in",
                size=14,
                color="#b3b3b3",
            ),
            ft.Divider(height=20, color="transparent"),
            email_input,
            password_input,
            primary_button("Sign In", on_click=handle_login),
            ft.Container(height=10),
            ft.Text("or", color="#b3b3b3"),
            ft.Container(height=5),
            ft.Row(
                [
                    ft.Icon(name=ft.Icons.G_TRANSLATE, color="white"),
                    ft.Text("Continue with Google", size=14, color="white"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Container(height=15),
            ft.TextButton(
                "Don't have an account? Sign up",
                on_click=go_to_signup,
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
