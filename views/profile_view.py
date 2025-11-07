import flet as ft
import sqlite3
from theme import set_theme, primary_button, input_field

DB_PATH = "database/otakuzone.db"

def get_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, username, birthdate, age, address, gender, bio
        FROM users WHERE id = ?
    """, (user_id,))
    data = cursor.fetchone()
    conn.close()
    return data

def update_user(user_id, name, username, birthdate, age, address, gender, bio):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET name=?, username=?, birthdate=?, age=?, address=?, gender=?, bio=?
        WHERE id=?
    """, (name, username, birthdate, age, address, gender, bio, user_id))
    conn.commit()
    conn.close()

def main(page: ft.Page, user_id=1):
    set_theme(page)
    page.title = "OtakuZone - Profile"
    page.scroll = "auto"

    user = get_user(user_id)
    if not user:
        page.add(ft.Text("User not found!", color="red"))
        return

    # Pre-fill user data
    name_field = input_field("Name")
    username_field = input_field("Username")
    birthdate_field = input_field("Birthdate (YYYY-MM-DD)")
    age_field = input_field("Age")
    address_field = input_field("Address")
    gender_dropdown = ft.Dropdown(
        label="Gender",
        options=[ft.dropdown.Option("Male"), ft.dropdown.Option("Female")],
        value=user[5] if user[5] else "Male",
        width=300
    )
    bio_field = input_field("Bio")
    bio_field.hint_text = "Introduce yourself to the OtakuZone Community."

    # Fill with existing data
    name_field.value = user[0] or ""
    username_field.value = user[1] or ""
    birthdate_field.value = user[2] or ""
    age_field.value = str(user[3] or "")
    address_field.value = user[4] or ""
    bio_field.value = user[6] or ""

    # Save handler
    def handle_save(e):
        update_user(
            user_id,
            name_field.value,
            username_field.value,
            birthdate_field.value,
            int(age_field.value) if age_field.value.isdigit() else 0,
            address_field.value,
            gender_dropdown.value,
            bio_field.value
        )

        dialog = ft.AlertDialog(
            title=ft.Text("✅ User Details Saved Successfully!"),
            on_dismiss=lambda e: page.go("/home")
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    # Back button
    def go_back(e):
        page.go("/home")

    header = ft.Row(
        [
            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=go_back),
            ft.Text("My Profile", size=22, weight="bold"),
        ],
        alignment="start",
    )

    layout = ft.Column(
        [
            header,
            ft.Divider(),
            name_field,
            username_field,
            birthdate_field,
            age_field,
            address_field,
            gender_dropdown,
            bio_field,
            ft.Container(primary_button("Save", handle_save), padding=10),
        ],
        horizontal_alignment="center",
        scroll="auto"
    )

    page.add(layout)

if __name__ == "__main__":
    ft.app(target=main)
