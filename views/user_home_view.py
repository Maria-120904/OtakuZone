import flet as ft
import sqlite3
from theme import set_theme, anime_card, input_field
from services.session_manager import SessionManager

DB_PATH = "database/otakuzone.db"


# Retrieve all anime
def get_all_anime():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, genre, category, image_path FROM anime")
    anime_list = cursor.fetchall()
    conn.close()
    return anime_list


def main(page: ft.Page):
    set_theme(page)
    page.title = "OtakuZone - Home"
    page.scroll = "auto"

    # Initialize session
    session = SessionManager(page)
    if not session.is_logged_in():
        page.go("/")
        return

    def toggle_nav(e):
        page.drawer.open = not page.drawer.open
        page.update()

    def show_anime_detail(anime):
        page.go(f"/detail/{anime[0]}")

    # Update anime list with search filter
    def update_anime_list(keyword=""):
        anime_items.controls.clear()
        anime_data = get_all_anime()
        keyword = keyword.lower()

        for anime in anime_data:
            if keyword and keyword not in anime[1].lower():
                continue
            anime_card_view = anime_card(anime[1], anime[2], anime[4], on_click=lambda e, a=anime: show_anime_detail(a))
            anime_items.controls.append(anime_card_view)

        page.update()

    def search_anime(e):
        update_anime_list(search_input.value)

    # Navigation handlers
    def navigate_to(route):
        def handler(e):
            page.go(route)
        return handler

    def handle_logout(e):
        session.logout()
        page.go("/")

    # Header bar
    search_input = ft.TextField(
        hint_text="Search anime...",
        width=200,
        on_submit=search_anime,
        text_style=ft.TextStyle(color="white"),
        cursor_color="#E50914"
    )

    header = ft.Row(
        [
            ft.IconButton(icon=ft.Icons.MENU, on_click=toggle_nav),
            ft.Text("OtakuZone", size=22, weight="bold", color="white"),
            search_input,
            ft.IconButton(icon=ft.Icons.ACCOUNT_CIRCLE, on_click=lambda e: page.go("/profile")),
        ],
        alignment="spaceBetween"
    )

    # Navigation Drawer
    page.drawer = ft.NavigationDrawer(
        controls=[
            ft.Container(ft.Text("Menu", size=18, weight="bold"), padding=10),
            ft.Container(ft.TextButton("Home", on_click=navigate_to("/home")), padding=5),
            ft.Container(ft.TextButton("My Favorites", on_click=navigate_to("/favorites")), padding=5),
            ft.Divider(),
            ft.Container(ft.TextButton("Logout", on_click=handle_logout), padding=5),
        ]
    )

    # Anime list container
    anime_items = ft.Row(wrap=True, spacing=15, alignment="center")
    update_anime_list()

    page.add(header, ft.Divider(color="#E50914"), anime_items)


if __name__ == "__main__":
    ft.app(target=main)
