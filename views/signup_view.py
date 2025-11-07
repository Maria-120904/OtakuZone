import flet as ft
import sqlite3
import bcrypt

def create_user_table():
    conn = sqlite3.connect("database/otakuzone.db")
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
    conn = sqlite3.connect("database/otakuzone.db")
    cursor = conn.cursor()
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute(
        "INSERT INTO users (name, username, email, password) VALUES (?, ?, ?, ?)",
        (name, username, email, hashed_pw)
    )
    conn.commit()
    conn.close()

def main(page: ft.Page):
    page.title = "OtakuZone - Sign Up"
    page.window_width = 400
    page.window_height = 650
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    create_user_table()

    name_input = ft.TextField(label="Full Name", width=300)
    username_input = ft.TextField(label="Username", width=300)
    email_input = ft.TextField(label="Email", width=300)
    password_input = ft.TextField(label="Password", width=300, password=True, can_reveal_password=True)
    message_text = ft.Text(value="", color="red")

    def handle_signup(e):
        if not all([name_input.value, username_input.value, email_input.value, password_input.value]):
            message_text.value = "Please fill all fields!"
            page.update()
            return
        
        try:
            add_user(name_input.value, username_input.value, email_input.value, password_input.value)
            message_text.value = "Account created! Redirecting..."
            message_text.color = "green"
            page.update()
            page.go("/login")
        except Exception as ex:
            message_text.value = f"Error: {str(ex)}"
            message_text.color = "red"
            page.update()

    def go_to_login(e):
        page.go("/login")

    layout = ft.Column(
        [
            ft.Text("Create Account", size=24, weight="bold"),
            name_input,
            username_input,
            email_input,
            password_input,
            ft.ElevatedButton("Sign Up", width=300, on_click=handle_signup),
            ft.TextButton("Already have an account? Login", on_click=go_to_login),
            message_text
        ],
        alignment="center",
        horizontal_alignment="center"
    )

    page.add(layout)