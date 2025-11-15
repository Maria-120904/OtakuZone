import flet as ft
import sqlite3
import bcrypt
from theme import set_theme, primary_button, input_field
from services.session_manager import SessionManager
from services.two_factor_service import is_2fa_enabled, toggle_2fa

DB_PATH = "database/otakuzone.db"


# Get user data
def get_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, username, birthdate, age, address, gender, bio, password, google_id, email
        FROM users WHERE id = ?
    """, (user_id,))
    data = cursor.fetchone()
    conn.close()
    return data


# Update user data
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


# Verify current password
def verify_password(user_id, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0]:
        return bcrypt.checkpw(password.encode("utf-8"), result[0])
    return False


# Update password
def update_password(user_id, new_password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    hashed_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
    cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_pw, user_id))
    conn.commit()
    conn.close()


# Main profile view
def main(page: ft.Page):
    set_theme(page)
    page.title = "OtakuZone - Profile"
    page.scroll = "auto"

    session = SessionManager(page)

    if not session.is_logged_in():
        page.go("/")
        return

    user_id = session.get_user_id()
    user = get_user(user_id)

    if not user:
        page.add(ft.Text("User not found!", color="red"))
        return

    # Check user type
    user_has_password = user[7] is not None
    is_google_user = user[8] is not None
    user_email = user[9]

    # Pre-fill fields
    name_field = input_field("Name")
    username_field = input_field("Username")
    birthdate_field = input_field("Birthdate (YYYY-MM-DD)")
    age_field = input_field("Age")
    address_field = input_field("Address")
    gender_dropdown = ft.Dropdown(
        label="Gender",
        options=[ft.dropdown.Option("Male"), ft.dropdown.Option("Female")],
        value=user[5] if user[5] else "Male",
        width=300,
        border_color="#E50914",
    )
    bio_field = input_field("Bio")
    bio_field.hint_text = "Introduce yourself to the OtakuZone Community."

    # Fill values
    name_field.value = user[0] or ""
    username_field.value = user[1] or ""
    birthdate_field.value = user[2] or ""
    age_field.value = str(user[3] or "")
    address_field.value = user[4] or ""
    bio_field.value = user[6] or ""

    # Message texts
    password_message = ft.Text(value="", size=12, text_align=ft.TextAlign.CENTER)
    twofa_message = ft.Text(value="", size=12, text_align=ft.TextAlign.CENTER)

    # Password containers
    change_password_container = ft.Column(
        visible=False, 
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
    set_password_container = ft.Column(
        visible=False, 
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER 
    )

    # Password inputs
    current_password_input = ft.TextField(
        label="Current Password",
        password=True,
        can_reveal_password=True,
        width=300,
        border_color="#E50914",
    )
    new_password_input = ft.TextField(
        label="New Password",
        password=True,
        can_reveal_password=True,
        width=300,
        border_color="#E50914",
    )
    confirm_new_password_input = ft.TextField(
        label="Confirm New Password",
        password=True,
        can_reveal_password=True,
        width=300,
        border_color="#E50914",
    )

    set_password_input = ft.TextField(
        label="Set Password",
        password=True,
        can_reveal_password=True,
        width=300,
        border_color="#E50914",
    )
    confirm_set_password_input = ft.TextField(
        label="Confirm Password",
        password=True,
        can_reveal_password=True,
        width=300,
        border_color="#E50914",
    )

    # Two-Factor Authentication Toggle
    twofa_enabled = is_2fa_enabled(user_email)
    
    twofa_switch = ft.Switch(
        value=twofa_enabled,
        active_color="#E50914",
        inactive_thumb_color="#b3b3b3",
    )
    
    twofa_status_text = ft.Text(
        value="Enabled" if twofa_enabled else "Disabled",
        size=14,
        color="green" if twofa_enabled else "red",
        weight="bold",
    )

    # 2FA Toggle Handler
    def handle_2fa_toggle(e):
        new_state = twofa_switch.value
        
        # Toggle 2FA
        toggle_2fa(user_id, new_state)
        
        # Update status text
        twofa_status_text.value = "Enabled" if new_state else "Disabled"
        twofa_status_text.color = "green" if new_state else "red"
        
        # Show message
        twofa_message.value = f"2FA has been {'enabled' if new_state else 'disabled'}!"
        twofa_message.color = "green"
        
        page.update()

    twofa_switch.on_change = handle_2fa_toggle

    # 2FA Container
    twofa_container = ft.Container(
        content=ft.Row(
            [
                ft.Text("Two-Factor Authentication:", size=14, weight="bold", color="white"),
                twofa_switch,
                twofa_status_text,
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        visible=True,
    )

    # Password handlers
    def show_change_password_inputs(e):
        change_password_container.visible = True
        set_password_container.visible = False
        password_button_container.visible = False
        password_message.value = ""
        page.update()

    def save_new_password(e):
        current_pw = current_password_input.value.strip()
        new_pw = new_password_input.value.strip()
        confirm_pw = confirm_new_password_input.value.strip()
        
        if not all([current_pw, new_pw, confirm_pw]):
            password_message.value = "All fields are required"
            password_message.color = "red"
            page.update()
            return
        
        if not verify_password(user_id, current_pw):
            password_message.value = "Current password is incorrect"
            password_message.color = "red"
            page.update()
            return
        
        if new_pw != confirm_pw:
            password_message.value = "New passwords do not match"
            password_message.color = "red"
            page.update()
            return
        
        if len(new_pw) < 6:
            password_message.value = "Password must be at least 6 characters"
            password_message.color = "red"
            page.update()
            return
        
        update_password(user_id, new_pw)
        password_message.value = "Password changed successfully!"
        password_message.color = "green"
        
        current_password_input.value = ""
        new_password_input.value = ""
        confirm_new_password_input.value = ""
        change_password_container.visible = False
        password_button_container.visible = True
        page.update()

    def cancel_change_password(e):
        current_password_input.value = ""
        new_password_input.value = ""
        confirm_new_password_input.value = ""
        change_password_container.visible = False
        password_button_container.visible = True
        password_message.value = ""
        page.update()

    def show_set_password_inputs(e):
        set_password_container.visible = True
        change_password_container.visible = False
        password_button_container.visible = False
        password_message.value = ""
        page.update()

    def save_password(e):
        new_pw = set_password_input.value.strip()
        confirm_pw = confirm_set_password_input.value.strip()
        
        if not new_pw or not confirm_pw:
            password_message.value = "All fields are required"
            password_message.color = "red"
            page.update()
            return
        
        if new_pw != confirm_pw:
            password_message.value = "Passwords do not match"
            password_message.color = "red"
            page.update()
            return
        
        if len(new_pw) < 6:
            password_message.value = "Password must be at least 6 characters"
            password_message.color = "red"
            page.update()
            return
        
        update_password(user_id, new_pw)
        password_message.value = "Password set successfully! You can now login with email and password."
        password_message.color = "green"
        
        set_password_input.value = ""
        confirm_set_password_input.value = ""
        set_password_container.visible = False
        
        password_button.text = "Change Password"
        password_button.on_click = show_change_password_inputs
        password_button_container.visible = True
        page.update()

    def cancel_set_password(e):
        set_password_input.value = ""
        confirm_set_password_input.value = ""
        set_password_container.visible = False
        password_button_container.visible = True
        password_message.value = ""
        page.update()

    password_button = ft.TextButton(
        text="Change Password" if user_has_password else "Set Password",
        style=ft.ButtonStyle(color="#E50914"),
        on_click=show_change_password_inputs if user_has_password else show_set_password_inputs,
    )
    
    password_button_container = ft.Container(
        content=ft.Row(
            [
                ft.Text("Security:", size=14, weight="bold", color="white"),
                ft.Container(
                    content=password_button,
                    border=ft.border.only(bottom=ft.border.BorderSide(1, "#E50914")),
                    padding=0,
                ),
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        visible=True,
    )

    change_password_container.controls = [
        ft.Container(height=10),
        ft.Text("Change Password", size=16, weight="bold", color="white", text_align=ft.TextAlign.CENTER),
        current_password_input,
        new_password_input,
        confirm_new_password_input,
        ft.Row(
            [
                ft.ElevatedButton(
                    "Save",
                    bgcolor="#E50914",
                    color="white",
                    width=140,
                    on_click=save_new_password,
                ),
                ft.TextButton(
                    "Cancel",
                    on_click=cancel_change_password,
                    style=ft.ButtonStyle(color="#b3b3b3"),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        ),
    ]

    set_password_container.controls = [
        ft.Container(height=10),
        ft.Text("Set Password", size=16, weight="bold", color="white", text_align=ft.TextAlign.CENTER),
        set_password_input,
        confirm_set_password_input,
        ft.Row(
            [
                ft.ElevatedButton(
                    "Save",
                    bgcolor="#E50914",
                    color="white",
                    width=140,
                    on_click=save_password,
                ),
                ft.TextButton(
                    "Cancel",
                    on_click=cancel_set_password,
                    style=ft.ButtonStyle(color="#b3b3b3"),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        ),
    ]

    def handle_save(e):
        update_user(
            user_id,
            name_field.value.strip(),
            username_field.value.strip(),
            birthdate_field.value.strip(),
            int(age_field.value) if age_field.value.isdigit() else 0,
            address_field.value.strip(),
            gender_dropdown.value,
            bio_field.value.strip(),
        )

        dialog = ft.AlertDialog(
            title=ft.Text("User details saved successfully!"),
            on_dismiss=lambda e: page.go("/home"),
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def go_back(e):
        page.go("/home")

    header = ft.Row(
        [
            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=go_back),
            ft.Text("My Profile", size=22, weight="bold", color="white"),
        ],
        alignment="start",
    )

    account_type_text = ft.Text(
        f"Account Type: {'Google Account' if is_google_user else 'Email/Password Account'}",
        size=12,
        color="#b3b3b3",
        italic=True,
    )

    layout = ft.Column(
        [
            header,
            ft.Divider(color="#E50914"),
            account_type_text,
            name_field,
            username_field,
            birthdate_field,
            age_field,
            address_field,
            gender_dropdown,
            bio_field,
            ft.Container(height=10),
            password_button_container,
            change_password_container,  
            set_password_container,     
            password_message,
            ft.Container(height=20),
            twofa_container,
            twofa_message,
            ft.Container(height=10),
            ft.Container(primary_button("Save Profile", handle_save), padding=10),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll="auto",
    )

    page.add(layout)

if __name__ == "__main__":
    ft.app(target=main)