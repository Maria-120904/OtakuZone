import flet as ft
import sqlite3
from theme import set_theme, primary_button
from services.session_manager import SessionManager

DB_PATH = "database/otakuzone.db"


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


def main(page: ft.Page):
    set_theme(page)
    page.title = "OtakuZone - Admin User Management"
    page.scroll = "auto"

    session = SessionManager(page)
    if not session.is_logged_in() or session.get_role() != "admin":
        page.go("/")
        return

    user_list_view = ft.Column(spacing=10)

    def refresh_user_list():
        user_list_view.controls.clear()
        users = get_all_users()
        for u in users:
            row = ft.Row(
                [
                    ft.Text(u[1], width=150, color="white"),
                    ft.Text(u[2], width=220, color="#b3b3b3"),
                    ft.Text(f"Role: {u[3]}", width=100, color="#E50914"),
                    ft.IconButton(icon=ft.Icons.DELETE, icon_color="red", on_click=lambda e, id=u[0]: handle_delete_user(id)),
                ],
                alignment="spaceBetween",
            )
            user_list_view.controls.append(row)
        page.update()

    def handle_delete_user(user_id):
        delete_user(user_id)
        refresh_user_list()

    def go_back(e):
        page.go("/admin/anime")

    header = ft.Row(
        [
            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=go_back),
            ft.Text("Admin - User Management", size=22, weight="bold", color="white"),
        ],
        alignment="start",
    )

    page.add(header, ft.Divider(color="#E50914"), user_list_view)
    refresh_user_list()


if __name__ == "__main__":
    ft.app(target=main)
