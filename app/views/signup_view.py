import flet as ft
import sqlite3
import bcrypt
from flet import (
    Page, Column, Container, Text, TextField, ElevatedButton, Row, TextButton, Icons, alignment, MainAxisAlignment
)

# Database connection helper
def create_user_table():
    conn = sqlite3.connect("app/database/otakuzone.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT,
        birthdate TEXT,
        age INTEGER,
        address TEXT,
        gender TEXT,
        bio TEXT,
        role TEXT DEFAULT 'user'
    )''')
    conn.commit()
    conn.close()

def add_user(name, username, email, password):
    conn = sqlite3.connect("app/database/otakuzone.db")
    cursor = conn.cursor()
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute(
        "INSERT INTO users (name, username, email, password) VALUES (?, ?, ?, ?)",
        (name, username, email, hashed_pw)
    )
    conn.commit()
    conn.close()

def main(page: Page):
    page.title = "OtakuZone - Sign Up"
    page.window_width = 400
    page.window_height = 650
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    name_input = TextField(label="Full Name", width=300)
    username_input = TextField(label="Username", width=300)
    email_input = TextField(label="Email", width=300)
    password_input = TextField(label="Password", width=300, password=True, can_reveal_password=True)
    message_text = Text(value="", color="red")

    def handle_signup(e):
        if not email_input.value or not password_input.value or not name_input.value or not username_input.value:
            message_text.value = "Please fill in all fields!"
            page.update()
            return

        try:
            add_user(name_input.value, username_input.value, email_input.value, password_input.value)
            page.dialog = ft.AlertDialog(
                title=ft.Text("User Created Successfully!"),
                on_dismiss=lambda e: print("Dialog dismissed.")
            )
            page.dialog.open = True
            page.update()
        except sqlite3.IntegrityError:
            message_text.value = "Email or Username already exists!"
            page.update()

    def go_to_login(e):
        print("Go to login page clicked (we’ll implement next).")

    # UI layout
    layout = Column(
        [
            Container(
                Text("Create New User Account", size=24, weight="bold"),
                alignment=alignment.center,
                padding=10
            ),
            Text("Already Registered? ", size=14),
            TextButton("Log in here", on_click=go_to_login),
            name_input,
            username_input,
            email_input,
            password_input,
            ElevatedButton("Sign Up", width=300, on_click=handle_signup),
            Row(
                [
                    ft.Icon(name=Icons.G_TRANSLATE, color="black"),
                    Text("Continue with Google", size=14)
                ],
                alignment=MainAxisAlignment.CENTER
            ),
            message_text
        ],
        alignment="center",
        horizontal_alignment="center"
    )

    page.add(layout)

# Run page standalone
if __name__ == "__main__":
    create_user_table()
    ft.app(target=main)
