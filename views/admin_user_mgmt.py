import flet as ft
import sqlite3
import bcrypt
import re
from theme import set_theme, primary_button, input_field
from services.session_manager import SessionManager

DB_PATH = "database/otakuzone.db"


# --- Database Helpers ---
def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, username, email, role FROM users")
    data = cursor.fetchall()
    conn.close()
    return data


def create_user(name, username, email, password, role="user"):
    """Create a new user with hashed password"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if email or username already exists
    cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", (email, username))
    existing = cursor.fetchone()
    
    if existing:
        conn.close()
        return False, "Email or username already exists"
    
    # Hash password
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


def update_user_role(user_id, new_role):
    """Update user role (user or admin)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
    conn.commit()
    conn.close()


def delete_user(user_id):
    """Delete a user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()


# --- Main Admin User Management View ---
def main(page: ft.Page):
    set_theme(page)
    page.title = "OtakuZone - Admin User Management"
    page.scroll = "auto"

    session = SessionManager(page)
    if not session.is_logged_in() or session.get_role() != "admin":
        page.go("/")
        return

    user_list_view = ft.Column(spacing=10)
    message_text = ft.Text(value="", size=14)

    # --- Refresh User List ---
    def refresh_user_list():
        user_list_view.controls.clear()
        users = get_all_users()
        
        # Add header row
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
                                tooltip="Edit Role",
                                on_click=lambda e, uid=user_id, uname=name, urole=role: open_edit_role_dialog(uid, uname, urole)
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

    # --- Delete User with Confirmation ---
    def confirm_delete_user(user_id, user_name):
        def delete_confirmed(e):
            delete_user(user_id)
            message_text.value = f"✅ User '{user_name}' deleted successfully"
            message_text.color = "green"
            dialog.open = False
            page.update()
            refresh_user_list()
        
        def cancel_delete(e):
            dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("⚠️ Confirm Delete"),
            content=ft.Text(f"Are you sure you want to delete user '{user_name}'?\n\nThis action cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_delete),
                ft.ElevatedButton("Delete", bgcolor="red", color="white", on_click=delete_confirmed),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()

    # --- Edit User Role Dialog ---
    def open_edit_role_dialog(user_id, user_name, current_role):
        role_dropdown = ft.Dropdown(
            label="Select Role",
            options=[
                ft.dropdown.Option("user"),
                ft.dropdown.Option("admin"),
            ],
            value=current_role,
            width=250,
            border_color="#E50914",
        )
        
        def save_role(e):
            new_role = role_dropdown.value
            update_user_role(user_id, new_role)
            message_text.value = f"✅ Role updated for '{user_name}' to {new_role.upper()}"
            message_text.color = "green"
            dialog.open = False
            page.update()
            refresh_user_list()
        
        def cancel_edit(e):
            dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"✏️ Edit Role for {user_name}"),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(f"Current Role: {current_role.upper()}", color="#b3b3b3", size=14),
                        ft.Divider(height=10),
                        role_dropdown,
                    ],
                    tight=True,
                    spacing=10,
                ),
                width=300,
                height=120,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_edit),
                ft.ElevatedButton("Save", bgcolor="#E50914", color="white", on_click=save_role),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()

    # --- Create New User Dialog ---
    def open_create_user_dialog(e):
        name_input = ft.TextField(
            label="Full Name",
            width=300,
            border_color="#E50914",
            autofocus=True,
        )
        username_input = ft.TextField(
            label="Username",
            width=300,
            border_color="#E50914",
        )
        email_input = ft.TextField(
            label="Email",
            width=300,
            border_color="#E50914",
        )
        password_input = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            width=300,
            border_color="#E50914",
        )
        role_dropdown = ft.Dropdown(
            label="Select Role",
            options=[
                ft.dropdown.Option("user"),
                ft.dropdown.Option("admin"),
            ],
            value="user",
            width=300,
            border_color="#E50914",
        )
        
        create_message = ft.Text(value="", size=12)
        
        def create_user_action(e):
            # Clear previous message
            create_message.value = ""
            
            # Validation
            if not all([name_input.value, username_input.value, email_input.value, password_input.value]):
                create_message.value = "❌ All fields are required"
                create_message.color = "red"
                page.update()
                return
            
            # Email validation
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email_input.value):
                create_message.value = "❌ Invalid email format"
                create_message.color = "red"
                page.update()
                return
            
            # Password length check
            if len(password_input.value) < 6:
                create_message.value = "❌ Password must be at least 6 characters"
                create_message.color = "red"
                page.update()
                return
            
            # Create user
            success, msg = create_user(
                name_input.value.strip(),
                username_input.value.strip(),
                email_input.value.strip(),
                password_input.value,
                role_dropdown.value
            )
            
            if success:
                message_text.value = f"✅ {msg}"
                message_text.color = "green"
                dialog.open = False
                page.update()
                refresh_user_list()
            else:
                create_message.value = f"❌ {msg}"
                create_message.color = "red"
                page.update()
        
        def cancel_create(e):
            dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("➕ Create New User"),
            content=ft.Container(
                content=ft.Column(
                    [
                        name_input,
                        username_input,
                        email_input,
                        password_input,
                        role_dropdown,
                        create_message,
                    ],
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO,
                ),
                width=350,
                height=380,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_create),
                ft.ElevatedButton("Create User", bgcolor="#E50914", color="white", on_click=create_user_action),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()

    # --- Navigation ---
    def go_back(e):
        page.go("/admin/anime")
    
    def logout(e):
        session.logout()
        page.go("/")

    # --- Header ---
    header = ft.Row(
        [
            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=go_back, tooltip="Back to Anime Management"),
            ft.Text("Admin - User Management", size=22, weight="bold", color="white"),
            ft.Container(expand=True),  # Spacer
            ft.Row(
                [
                    primary_button("Create User", on_click=open_create_user_dialog, width=150),
                    ft.IconButton(
                        icon=ft.Icons.LOGOUT,
                        icon_color="red",
                        tooltip="Logout",
                        on_click=logout
                    ),
                ],
                spacing=10
            ),
        ],
        alignment="spaceBetween",
    )

    # --- Layout ---
    page.add(
        header,
        ft.Divider(color="#E50914"),
        message_text,
        ft.Divider(height=10, color="transparent"),
        user_list_view
    )
    
    refresh_user_list()


if __name__ == "__main__":
    ft.app(target=main)