import flet as ft
from theme import set_theme
from services.session_manager import SessionManager
from views.admin_anime_mgmt import anime_management_view  # ✅ Changed from relative to absolute import
from views.admin_user_mgmt import user_management_view  # ✅ Changed from relative to absolute import

def main(page: ft.Page):
    set_theme(page)
    page.title = "OtakuZone - Admin Dashboard"
    page.scroll = "auto"
    page.window_resizable = True

    session = SessionManager(page)
    if not session.is_logged_in() or session.get_role() != "admin":
        page.go("/")
        return

    # Clear existing controls before rendering admin view
    page.controls.clear()

    tab_index = 0  # 0: Anime, 1: User

    content_area = ft.Container(expand=True, padding=ft.padding.symmetric(horizontal=20))

    def switch_tab(e):
        nonlocal tab_index
        tab_index = e.control.selected_index
        update_content()

    def update_content():
        if tab_index == 0:
            content_area.content = anime_management_view(page)
        else:
            content_area.content = user_management_view(page)
        page.update()

    def handle_logout(e):
        session.logout()
        page.go("/login")

    # Header with title on left and logout on right
    header = ft.Row(
        [
            ft.Text("Admin Dashboard", size=22, weight="bold", color="white"),
            ft.IconButton(
                icon=ft.Icons.LOGOUT,
                icon_color="white",
                tooltip="Logout",
                on_click=handle_logout
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
        height=60,
    )

    # Nav bar (tabs) below header, left-aligned
    nav_bar = ft.Tabs(
        selected_index=tab_index,
        on_change=switch_tab,
        tabs=[
            ft.Tab(text="Anime Management"),
            ft.Tab(text="User Management"),
        ],
        indicator_color="#E50914",
        label_color="white",
        unselected_label_color="#b3b3b3",
        expand=False,
        tab_alignment="start"
    )

    page.add(
        ft.Container(header, bgcolor="#18191A", padding=ft.padding.symmetric(horizontal=20, vertical=10)),
        ft.Container(nav_bar, padding=ft.padding.symmetric(horizontal=20)),
        
        content_area,
    )

    update_content()

if __name__ == "__main__":
    ft.app(target=main)