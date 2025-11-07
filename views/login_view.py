import flet as ft
import sqlite3
import bcrypt

def get_user_by_email(email):
    conn = sqlite3.connect("database/otakuzone.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, username, email, password, role FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def main(page: ft.Page):
    page.title = "OtakuZone - Login"
    page.window_width = 400
    page.window_height = 650
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    email_input = ft.TextField(label="Email", width=300)
    password_input = ft.TextField(label="Password", width=300, password=True, can_reveal_password=True)
    message_text = ft.Text(value="", color="red")

    def handle_login(e):
        if not email_input.value or not password_input.value:
            message_text.value = "Please fill in all fields!"
            page.update()
            return

        user = get_user_by_email(email_input.value)
        if user:
            stored_hash = user[4]
            if bcrypt.checkpw(password_input.value.encode('utf-8'), stored_hash):
                # Store session
                page.session_data = {
                    "user_id": user[0],
                    "username": user[2],
                    "role": user[5]
                }
                # Navigate based on role
                if user[5] == "admin":
                    page.go("/admin/anime")
                else:
                    page.go("/home")
            else:
                message_text.value = "Incorrect password!"
        else:
            message_text.value = "User not found!"
        page.update()

    def go_to_signup(e):
        page.go("/signup")

    layout = ft.Column(
        [
            ft.Container(
                ft.Text("Welcome back!", size=24, weight="bold"),
                alignment=ft.alignment.center,
                padding=10
            ),
            ft.Text("Use your email and password to login", size=14),
            email_input,
            password_input,
            ft.ElevatedButton("Sign In", width=300, on_click=handle_login),
            ft.Row(
                [
                    ft.Icon(name=ft.Icons.G_TRANSLATE, color="black"),
                    ft.Text("Continue with Google", size=14)
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            ft.TextButton("Don't have an account? Sign up", on_click=go_to_signup),
            message_text
        ],
        alignment="center",
        horizontal_alignment="center"
    )

    page.add(layout)

if __name__ == "__main__":
    ft.app(target=main)