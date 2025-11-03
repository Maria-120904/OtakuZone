import flet as ft
import sqlite3
import bcrypt
from flet import Page, Text, TextField, ElevatedButton, Row, TextButton, Container, Column, Icons, alignment, MainAxisAlignment

# Database helper
def get_user_by_email(email):
    conn = sqlite3.connect("app/database/otakuzone.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, username, email, password, role FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def main(page: Page):
    page.title = "OtakuZone - Login"
    page.window_width = 400
    page.window_height = 650
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    email_input = TextField(label="Email", width=300)
    password_input = TextField(label="Password", width=300, password=True, can_reveal_password=True)
    message_text = Text(value="", color="red")

    def handle_login(e):
        if not email_input.value or not password_input.value:
            message_text.value = "Please fill in all fields!"
            page.update()
            return

        user = get_user_by_email(email_input.value)
        if user:
            stored_hash = user[4]
            if bcrypt.checkpw(password_input.value.encode('utf-8'), stored_hash):
                message_text.value = ""
                # Placeholder for navigation to home page
                role = user[5]
                if role == "admin":
                    ft.AlertDialog(title=ft.Text("Welcome Admin!"))
                    print("✅ Redirect to Admin Home Page here")
                else:
                    ft.AlertDialog(title=ft.Text("Welcome User!"))
                    print("✅ Redirect to User Home Page here")

                page.dialog = ft.AlertDialog(
                    title=ft.Text(f"Welcome back, {user[1]}!"),
                    on_dismiss=lambda e: print("Dialog closed."),
                )
                page.dialog.open = True
                page.update()
            else:
                message_text.value = "Incorrect password!"
        else:
            message_text.value = "User not found!"
        page.update()

    def go_to_signup(e):
        print("Go to Sign-Up Page clicked (we’ll link later).")

    layout = Column(
        [
            Container(
                Text("Welcome back!", size=24, weight="bold"),
                alignment=alignment.center,
                padding=10
            ),
            Text("Use your email and password to login", size=14),
            email_input,
            password_input,
            ElevatedButton("Sign In", width=300, on_click=handle_login),
            Row(
                [
                    ft.Icon(name=Icons.G_TRANSLATE, color="black"),
                    Text("Continue with Google", size=14)
                ],
                alignment=MainAxisAlignment.CENTER
            ),
            TextButton("Don't have an account? Sign up", on_click=go_to_signup),
            message_text
        ],
        alignment="center",
        horizontal_alignment="center"
    )

    page.add(layout)

if __name__ == "__main__":
    ft.app(target=main)
