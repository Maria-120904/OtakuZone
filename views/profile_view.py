import flet as ft
import sqlite3
import bcrypt
import os
from PIL import Image
from theme import set_theme, primary_button, input_field
from services.session_manager import SessionManager
from services.two_factor_service import is_2fa_enabled, toggle_2fa

DB_PATH = "database/otakuzone.db"
PROFILE_DIR = "assets/profile"

os.makedirs(PROFILE_DIR, exist_ok=True)

def get_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, username, birthdate, age, address, gender, bio, password, google_id, email, profile_image
        FROM users WHERE id = ?
    """, (user_id,))
    data = cursor.fetchone()
    conn.close()
    return data

def update_user(user_id, name, username, birthdate, age, address, gender, bio, profile_image=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if profile_image is not None:
        cursor.execute("""
            UPDATE users
            SET name=?, username=?, birthdate=?, age=?, address=?, gender=?, bio=?, profile_image=?
            WHERE id=?
        """, (name, username, birthdate, age, address, gender, bio, profile_image, user_id))
    else:
        cursor.execute("""
            UPDATE users
            SET name=?, username=?, birthdate=?, age=?, address=?, gender=?, bio=?
            WHERE id=?
        """, (name, username, birthdate, age, address, gender, bio, user_id))
    conn.commit()
    conn.close()

def verify_password(user_id, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result and result[0]:
        return bcrypt.checkpw(password.encode("utf-8"), result[0])
    return False

def update_password(user_id, new_password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    hashed_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
    cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_pw, user_id))
    conn.commit()
    conn.close()

def main(page: ft.Page):
    set_theme(page)
    page.title = "OtakuZone - Profile"
    page.scroll = "auto"
    page.window.width = 400
    page.window.height = 700
    page.window.resizable = False

    session = SessionManager(page)
    if not session.is_logged_in():
        page.go("/")
        return

    user_id = session.get_user_id()
    user = get_user(user_id)
    if not user:
        page.add(ft.Text("User not found!", color="red", width=360))
        return

    name, username, birthdate, age, address, gender, bio, password, google_id, email, profile_image = user
    profile_img_path = profile_image if profile_image and os.path.exists(profile_image) else None
    selected_profile_img = [profile_img_path]

    def get_avatar():
        if selected_profile_img[0] and os.path.exists(selected_profile_img[0]):
            return ft.Image(
                src=selected_profile_img[0],
                width=128,
                height=128,
                fit="cover",
                border_radius=64,
            )
        else:
            letter = (username or name or "U")[0].upper()
            return ft.Container(
                content=ft.Text(letter, size=48, color="white", weight="bold"),
                width=128,
                height=128,
                bgcolor="#E50914",
                border_radius=64,
                alignment=ft.alignment.center,
            )

    avatar = get_avatar()
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)

    def on_file_result(e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            file = e.files[0]
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in [".jpg", ".jpeg", ".png"]:
                page.snack_bar = ft.SnackBar(ft.Text("Only .jpg and .png files allowed!"))
                page.snack_bar.open = True
                page.update()
                return
            temp_path = os.path.join(PROFILE_DIR, f"temp_user_{user_id}{ext}")
            try:
                img = Image.open(file.path)
                img = img.convert("RGB")
                img = img.resize((256, 256))
                img.save(temp_path)
                selected_profile_img[0] = temp_path
                avatar_container.content = get_avatar()
                page.update()
            except Exception:
                page.snack_bar = ft.SnackBar(ft.Text("Failed to process image."))
                page.snack_bar.open = True
                page.update()

    file_picker.on_result = on_file_result

    def pick_profile_image(e):
        file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["jpg", "jpeg", "png"]
        )

    avatar_container = ft.Container(
        content=avatar,
        width=128,
        height=128,
        alignment=ft.alignment.center,
        margin=ft.margin.only(bottom=10),
    )

    change_profile_btn = ft.ElevatedButton(
        "Change Profile",
        icon=ft.Icons.EDIT,
        bgcolor="#E50914",
        color="white",
        width=160,
        on_click=pick_profile_image,
    )

    # Pre-fill fields
    name_field = input_field("Name", width=360)
    username_field = input_field("Username", width=360)
    birthdate_field = input_field("Birthdate (YYYY-MM-DD)", width=None, expand=1)
    age_field = input_field("Age", width=None, expand=1)
    address_field = input_field("Address", width=None, expand=1)
    gender_dropdown = ft.Dropdown(
        label="Gender",
        options=[ft.dropdown.Option("Male"), ft.dropdown.Option("Female")],
        value=gender if gender else "Male",
        width=None,
        expand=1,
        border_color="#E50914",
    )
    bio_field = input_field(
        "Bio",
        width=360,
        height=110,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=16),
        multiline=True,
        min_lines=6,
        max_lines=100
    )
    bio_field.hint_text = "Introduce yourself to the OtakuZone Community."
    name_field.value = name or ""
    username_field.value = username or ""
    birthdate_field.value = birthdate or ""
    age_field.value = str(age or "")
    address_field.value = address or ""
    bio_field.value = bio or ""

    password_message = ft.Text(value="", size=12, text_align=ft.TextAlign.CENTER, width=360)

    change_password_container = ft.Column(
        visible=False, 
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        width=360
    )
    set_password_container = ft.Column(
        visible=False, 
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        width=360
    )

    current_password_input = ft.TextField(
        label="Current Password",
        password=True,
        can_reveal_password=True,
        width=360,
        border_color="#E50914",
    )
    new_password_input = ft.TextField(
        label="New Password",
        password=True,
        can_reveal_password=True,
        width=360,
        border_color="#E50914",
    )
    confirm_new_password_input = ft.TextField(
        label="Confirm New Password",
        password=True,
        can_reveal_password=True,
        width=360,
        border_color="#E50914",
    )
    set_password_input = ft.TextField(
        label="Set Password",
        password=True,
        can_reveal_password=True,
        width=360,
        border_color="#E50914",
    )
    confirm_set_password_input = ft.TextField(
        label="Confirm Password",
        password=True,
        can_reveal_password=True,
        width=360,
        border_color="#E50914",
    )

    twofa_enabled = is_2fa_enabled(email)
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

    def handle_2fa_toggle(e):
        new_state = twofa_switch.value
        toggle_2fa(user_id, new_state)
        twofa_status_text.value = "Enabled" if new_state else "Disabled"
        twofa_status_text.color = "green" if new_state else "red"
        page.update()

    twofa_switch.on_change = handle_2fa_toggle

    # State for showing/hiding the change password button
    show_change_password_btn = ft.Ref[ft.Text]()

    def show_change_password_inputs(e):
        change_password_container.visible = True
        set_password_container.visible = False
        show_change_password_btn.current.visible = False
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
        show_change_password_btn.current.visible = True
        page.update()

    def cancel_change_password(e):
        current_password_input.value = ""
        new_password_input.value = ""
        confirm_new_password_input.value = ""
        change_password_container.visible = False
        show_change_password_btn.current.visible = True
        password_message.value = ""
        page.update()

    def show_set_password_inputs(e):
        set_password_container.visible = True
        change_password_container.visible = False
        show_change_password_btn.current.visible = False
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
        password_button.value = "Change Password"
        password_button.on_click = show_change_password_inputs
        show_change_password_btn.current.visible = True
        page.update()

    def cancel_set_password(e):
        set_password_input.value = ""
        confirm_set_password_input.value = ""
        set_password_container.visible = False
        show_change_password_btn.current.visible = True
        password_message.value = ""
        page.update()

    password_button = ft.GestureDetector(
        content=ft.Text(
            "Change Password" if password is not None else "Set Password",
            color="#E50914",
            size=12,
            weight="bold",
            width=160,
            selectable=False,
        ),
        on_tap=show_change_password_inputs if password is not None else show_set_password_inputs,
        mouse_cursor="click",
        ref=show_change_password_btn,
        visible=True
    )

    twofa_container = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Two-Factor Authentication:", size=14, weight="bold", color="white"),
                        twofa_switch,
                    ],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER,
                    width=360,
                ),
                ft.Row(
                    [twofa_status_text],
                    alignment=ft.MainAxisAlignment.CENTER,
                    width=360,
                ),
            ],
            spacing=2,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        visible=True,
        width=400,
        padding=ft.padding.symmetric(horizontal=20)
    )

    change_password_container.controls = [
        ft.Container(height=10),
        ft.Text("Change Password", size=16, weight="bold", color="white", text_align=ft.TextAlign.CENTER, width=360),
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
                    width=80,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
            width=360,
        ),
    ]

    set_password_container.controls = [
        ft.Container(height=10),
        ft.Text("Set Password", size=16, weight="bold", color="white", text_align=ft.TextAlign.CENTER, width=360),
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
                    width=80,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
            width=360,
        ),
    ]

    def handle_save(e):
        final_profile_img = profile_img_path
        if selected_profile_img[0] and selected_profile_img[0] != profile_img_path:
            ext = os.path.splitext(selected_profile_img[0])[1].lower()
            final_profile_img = os.path.join(PROFILE_DIR, f"user_{user_id}{ext}")
            try:
                os.replace(selected_profile_img[0], final_profile_img)
            except Exception:
                import shutil
                shutil.copy(selected_profile_img[0], final_profile_img)
            selected_profile_img[0] = final_profile_img

        update_user(
            user_id,
            name_field.value.strip(),
            username_field.value.strip(),
            birthdate_field.value.strip(),
            int(age_field.value) if age_field.value.isdigit() else 0,
            address_field.value.strip(),
            gender_dropdown.value,
            bio_field.value.strip(),
            final_profile_img
        )
        page.go("/home")  # Go to home page immediately

    def go_back(e):
        page.go("/home")

    header = ft.Column(
        [
            ft.Row(
                [
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=go_back),
                    ft.Text("My Profile", size=22, weight="bold", color="white"),
                ],
                alignment="start",
            ),
            ft.Divider(color="#E50914", height=1),
        ],
        spacing=10,
        width=400,
    )

    layout = ft.Column(
        [
            header, 
            ft.Container(
                ft.Column(
                    [
                        avatar_container,
                        ft.Row([change_profile_btn], alignment="center"),
                    ],
                    horizontal_alignment="center",
                    alignment="center",
                    spacing=5,
                ),
                alignment=ft.alignment.center,
                width=400,
                padding=ft.padding.only(top=10, bottom=10, left=20, right=20),
            ),
            ft.Container(
                ft.Column(
                    [
                        name_field,
                        username_field,
                        ft.Row(
                            [birthdate_field, age_field],
                            alignment="spaceBetween",
                            spacing=10,
                            width=360,
                        ),
                        ft.Row(
                            [address_field, gender_dropdown],
                            alignment="spaceBetween",
                            spacing=10,
                            width=360,
                        ),
                        bio_field,
                        password_button, 
                        ft.Container(height=8),
                        twofa_container,  
                    ],
                    spacing=10,
                ),
                padding=ft.padding.symmetric(horizontal=20),
                width=400,
            ),
            ft.Container(change_password_container, padding=ft.padding.symmetric(horizontal=20), width=400),
            ft.Container(set_password_container, padding=ft.padding.symmetric(horizontal=20), width=400),
            ft.Container(password_message, padding=ft.padding.symmetric(horizontal=20), width=400),
            ft.Container(primary_button("Save Profile", handle_save, width=360), padding=ft.padding.symmetric(horizontal=20, vertical=4), width=400),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll="auto",
        width=400,
        spacing=10,
    )

    page.add(layout)

if __name__ == "__main__":
    ft.app(target=main)