import flet as ft
import sqlite3
import bcrypt
import re
import threading
from theme import primary_button
from services.session_manager import SessionManager
from services.email_service import (
    generate_verification_code,
    send_admin_user_verification_email,
    verify_code,
    resend_verification_code
)

DB_PATH = "database/otakuzone.db"

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, username, email, role FROM users")
    data = cursor.fetchall()
    conn.close()
    return data

def create_user(name, username, email, password, role="user"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", (email, username))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return False, "Email or username already exists"
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    try:
        cursor.execute("""
            INSERT INTO users (name, username, email, password, role)
            VALUES (?, ?, ?, ?, ?)
        """, (name, username, email, hashed_pw, role))
        conn.commit()
        conn.close()
        return True, "User created successfully"
    except Exception as e:
        conn.close()
        return False, str(e)

def update_user(user_id, name, username, role):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ? AND id != ?", (username, user_id))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return False, "Username already exists"
    
    cursor.execute("""
        UPDATE users 
        SET name = ?, username = ?, role = ? 
        WHERE id = ?
    """, (name, username, role, user_id))
    conn.commit()
    conn.close()
    return True, "User updated successfully"

def delete_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

def user_management_view(page: ft.Page):
    session = SessionManager(page)
    if not session.is_logged_in() or session.get_role() != "admin":
        return ft.Text("Unauthorized", color="red")

    user_list_view = ft.Column(spacing=10)

    def refresh_user_list():
        user_list_view.controls.clear()
        
        # ✅ Table header
        header = ft.Row(
            [
                ft.Text("Name", width=120, weight="bold", color="white"),
                ft.Text("Username", width=100, weight="bold", color="white"),
                ft.Text("Email", width=150, weight="bold", color="white"),
                ft.Text("Role", width=60, weight="bold", color="white"),
                ft.Text("Actions", width=100, weight="bold", color="white"),
            ],
            alignment="start",
        )
        user_list_view.controls.append(header)
        user_list_view.controls.append(ft.Divider(color="#E50914"))
        
        users = get_all_users()
        if not users:
            user_list_view.controls.append(
                ft.Text("No users found.", color="#b3b3b3", italic=True)
            )
        for u in users:
            user_id, name, username, email, role = u
            row = ft.Row(
                [
                    ft.Text(name or "N/A", width=120, color="white"),
                    ft.Text(username or "N/A", width=100, color="#b3b3b3"),
                    ft.Text(email or "N/A", width=150, color="#b3b3b3"),
                    ft.Text(role.upper(), width=60, color="#E50914" if role == "admin" else "#00ff00"),
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_color="#E50914",
                                icon_size=20,
                                tooltip="Edit User",
                                on_click=lambda e, uid=user_id, uname=name, uusername=username, urole=role: open_edit_user_dialog(uid, uname, uusername, urole)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color="red",
                                icon_size=20,
                                tooltip="Delete User",
                                on_click=lambda e, uid=user_id, uname=name: confirm_delete_user(uid, uname)
                            ),
                        ],
                        spacing=5
                    ),
                ],
                alignment="start",
            )
            user_list_view.controls.append(row)
        page.update()

    def confirm_delete_user(user_id, user_name):
        def delete_confirmed(e):
            delete_user(user_id)
            dialog.open = False
            page.update()
            refresh_user_list()
        
        def cancel_delete(e):
            dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Delete"),
            content=ft.Text(f"Are you sure you want to delete user '{user_name}'?\n\nThis action cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_delete),
                ft.ElevatedButton("Delete", bgcolor="red", color="white", on_click=delete_confirmed),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def open_edit_user_dialog(user_id, user_name, user_username, current_role):
        name_input = ft.TextField(
            label="Full Name",
            value=user_name or "",
            width=350,
            border_color="#E50914",
        )
        
        username_input = ft.TextField(
            label="Username",
            value=user_username or "",
            width=350,
            border_color="#E50914",
        )
        
        role_dropdown = ft.Dropdown(
            label="Select Role",
            options=[
                ft.dropdown.Option("user", "User"),
                ft.dropdown.Option("admin", "Admin"),
            ],
            value=current_role,
            width=350,
            border_color="#E50914",
        )
        
        edit_message = ft.Text(value="", size=12, text_align="center")
        
        def save_user(e):
            new_name = name_input.value.strip()
            new_username = username_input.value.strip()
            new_role = role_dropdown.value
            
            if not new_name:
                edit_message.value = "❌ Full Name is required"
                edit_message.color = "red"
                page.update()
                return
            
            if not new_username:
                edit_message.value = "❌ Username is required"
                edit_message.color = "red"
                page.update()
                return
            
            success, msg = update_user(user_id, new_name, new_username, new_role)
            
            if success:
                dialog.open = False
                page.update()
                refresh_user_list()
            else:
                edit_message.value = f"❌ {msg}"
                edit_message.color = "red"
                page.update()
        
        def cancel_edit(e):
            dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Container(
                ft.Text("Edit User", size=18, weight="bold", color="white"),
                alignment=ft.alignment.center,
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        name_input,
                        username_input,
                        role_dropdown,
                        edit_message,
                    ],
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO,
                ),
                width=370,
                height=190,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_edit),
                ft.ElevatedButton("Save", bgcolor="#E50914", color="white", on_click=save_user),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def open_create_user_dialog(e=None):
        """Create new user with email verification"""
        
        name_input = ft.TextField(
            label="Full Name",
            width=350,
            border_color="#E50914",
        )
        
        username_input = ft.TextField(
            label="Username",
            width=350,
            border_color="#E50914",
        )
        
        email_input = ft.TextField(
            label="Email",
            width=350,
            border_color="#E50914",
        )
        
        password_input = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            width=350,
            border_color="#E50914",
        )
        
        confirm_password_input = ft.TextField(
            label="Confirm Password",
            password=True,
            can_reveal_password=True,
            width=350,
            border_color="#E50914",
        )
        
        role_dropdown = ft.Dropdown(
            label="Select Role",
            options=[
                ft.dropdown.Option("user", "User"),
                ft.dropdown.Option("admin", "Admin"),
            ],
            value="user",
            width=350,
            border_color="#E50914",
        )
        
        send_code_btn_container = ft.Container(
            content=ft.ElevatedButton(
                "Send Verification Code",
                bgcolor="#E50914",
                color="white",
                width=350,
            ),
            visible=True,
        )
        
        verification_code_input = ft.TextField(
            label="Enter 6-digit code",
            width=350,
            max_length=6,
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color="#E50914",
        )
        
        code_input_container = ft.Container(
            content=verification_code_input,
            visible=False,
        )
        
        resend_verify_row = ft.Row(
            [
                ft.ElevatedButton(
                    "Resend Code",
                    bgcolor="#555555",
                    color="white",
                    width=170,
                ),
                ft.ElevatedButton(
                    "Verify",
                    bgcolor="#E50914",
                    color="white",
                    width=170,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
            visible=False,
        )
        
        form_inputs_container = ft.Container(
            content=ft.Column([
                name_input,
                username_input,
                email_input,
                password_input,
                confirm_password_input,
                role_dropdown,
            ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            visible=True,
        )
        
        create_message = ft.Text(value="", size=12, text_align="center")
        
        temp_data = {}
        
        def is_valid_email(email_str):
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return re.match(pattern, email_str) is not None
        
        def is_valid_password(password):
            if len(password) < 6:
                return False, "Password must be at least 6 characters"
            if not any(c.isupper() for c in password):
                return False, "Password must contain at least one uppercase letter"
            if not any(c.islower() for c in password):
                return False, "Password must contain at least one lowercase letter"
            return True, ""
        
        def send_verification(ev):
            create_message.value = ""
            
            if not all([name_input.value, username_input.value, email_input.value, password_input.value, confirm_password_input.value]):
                create_message.value = "❌ All fields are required!"
                create_message.color = "red"
                page.update()
                return
            
            if not is_valid_email(email_input.value):
                create_message.value = "❌ Invalid email format!"
                create_message.color = "red"
                page.update()
                return
            
            if password_input.value != confirm_password_input.value:
                create_message.value = "❌ Passwords do not match!"
                create_message.color = "red"
                page.update()
                return
            
            valid, msg = is_valid_password(password_input.value)
            if not valid:
                create_message.value = f"❌ {msg}"
                create_message.color = "red"
                page.update()
                return
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", (email_input.value.strip(), username_input.value.strip()))
            existing = cursor.fetchone()
            conn.close()
            
            if existing:
                create_message.value = "❌ Email or username already exists!"
                create_message.color = "red"
                page.update()
                return
            
            temp_data["name"] = name_input.value.strip()
            temp_data["username"] = username_input.value.strip()
            temp_data["email"] = email_input.value.strip()
            temp_data["password"] = password_input.value
            temp_data["role"] = role_dropdown.value
            
            create_message.value = "📧 Sending verification code..."
            create_message.color = "blue"
            send_code_btn_container.content.disabled = True
            page.update()
            
            def send_email_thread():
                code = generate_verification_code()
                print(f"🔑 Generated code: {code} for {temp_data['email']}")
                
                success, error = send_admin_user_verification_email(temp_data["email"], code)
                
                if success:
                    print(f"✅ Email sent successfully to {temp_data['email']}")
                    create_message.value = "✅ Verification code sent! Check your email."
                    create_message.color = "green"
                    
                    form_inputs_container.visible = False
                    send_code_btn_container.visible = False
                    code_input_container.visible = True
                    resend_verify_row.visible = True
                    save_btn.disabled = False
                    
                    page.update()
                else:
                    print(f"❌ Email send failed: {error}")
                    create_message.value = f"❌ Failed to send email: {error or 'Unknown error'}"
                    create_message.color = "red"
                    send_code_btn_container.content.disabled = False
                    page.update()
            
            thread = threading.Thread(target=send_email_thread, daemon=True)
            thread.start()
        
        def verify_code_action(ev):
            """Verify the code"""
            entered_code = verification_code_input.value
            
            if not entered_code or len(entered_code) != 6:
                create_message.value = "❌ Please enter the 6-digit code"
                create_message.color = "red"
                page.update()
                return
            
            is_valid = verify_code(temp_data["email"], entered_code)
            
            if is_valid:
                create_message.value = "✅ Code verified! Click Save to create user."
                create_message.color = "green"
                temp_data["verified"] = True
                page.update()
            else:
                create_message.value = "❌ Invalid or expired verification code"
                create_message.color = "red"
                page.update()
        
        def save_user(ev):
            """Save user (only if verified)"""
            if not temp_data.get("verified"):
                create_message.value = "❌ Please verify the code first"
                create_message.color = "red"
                page.update()
                return
            
            success, msg = create_user(
                temp_data["name"],
                temp_data["username"],
                temp_data["email"],
                temp_data["password"],
                temp_data["role"]
            )
            
            if success:
                dialog.open = False
                page.update()
                refresh_user_list()
            else:
                create_message.value = f"❌ {msg}"
                create_message.color = "red"
                page.update()
        
        def resend_code_action(ev):
            """Resend verification code"""
            create_message.value = "📧 Resending code..."
            create_message.color = "blue"
            page.update()
            
            def resend_thread():
                if resend_verification_code(temp_data["email"]):
                    create_message.value = "✅ New code sent to email"
                    create_message.color = "green"
                else:
                    create_message.value = "❌ Failed to send code"
                    create_message.color = "red"
                page.update()
            
            thread = threading.Thread(target=resend_thread, daemon=True)
            thread.start()
        
        send_code_btn_container.content.on_click = send_verification
        resend_verify_row.controls[0].on_click = resend_code_action
        resend_verify_row.controls[1].on_click = verify_code_action
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        save_btn = ft.ElevatedButton(
            "Save",
            bgcolor="#E50914",
            color="white",
            on_click=save_user,
            disabled=True,
        )
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Container(
                ft.Text("Create New User", size=18, weight="bold", color="white"),
                alignment=ft.alignment.center,
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Fill in the details below", size=12, color="#b3b3b3"),
                        form_inputs_container,
                        send_code_btn_container,
                        code_input_container,
                        resend_verify_row,
                        create_message,
                    ],
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO,
                ),
                width=380,
                height=440,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                save_btn,
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # ✅ NEW: Title and Create User button in one row (same as Anime Management)
    title_and_add_row = ft.Row(
        [
            ft.Text("Manage Users", size=16, weight="bold", color="white"),
            ft.Container(expand=True),  # Spacer
            primary_button("Create User", on_click=open_create_user_dialog, width=150),
        ],
        alignment="spaceBetween",
        vertical_alignment="center",
    )

    layout = ft.Column(
        [
            title_and_add_row, 
            ft.Divider(color="#E50914", height=1),
            user_list_view,  
        ],
        spacing=10,
        expand=True,
        scroll="auto"
    )

    refresh_user_list()
    return layout