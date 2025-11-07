import flet as ft
import sqlite3

DB_PATH = "database/otakuzone.db"

# --- DATABASE HELPERS ---
def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, role FROM users")
    data = cursor.fetchall()
    conn.close()
    return data

def delete_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

# --- MAIN PAGE FUNCTION ---
def main(page: ft.Page):
    page.title = "OtakuZone - Admin User Management"
    page.scroll = "auto"

    user_list_view = ft.Column(spacing=10)

    def refresh_user_list():
        user_list_view.controls.clear()
        users = get_all_users()
        for u in users:
            row = ft.Row(
                [
                    ft.Text(u[1], width=150),
                    ft.Text(u[2], width=220),
                    ft.Text(f"Role: {u[3]}", width=120),
                    ft.IconButton(icon=ft.Icons.DELETE, icon_color="red", on_click=lambda e, id=u[0]: handle_delete_user(id)),
                ],
                alignment="spaceBetween"
            )
            user_list_view.controls.append(row)
        page.update()

    def handle_delete_user(user_id):
        delete_user(user_id)
        refresh_user_list()

    header = ft.Row(
        [
            ft.Text("Admin - User Management", size=22, weight="bold"),
        ],
        alignment="start"
    )

    page.add(header, ft.Divider(), user_list_view)
    refresh_user_list()

if __name__ == "__main__":
    ft.app(target=main)
