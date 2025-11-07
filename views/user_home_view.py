import flet as ft
import sqlite3

def get_all_anime():
    conn = sqlite3.connect("database/otakuzone.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, genre, category, image_path FROM anime")
    anime_list = cursor.fetchall()
    conn.close()
    return anime_list

def main(page: ft.Page, user_id=None):
    page.title = "OtakuZone - Home"
    page.theme_mode = "light"
    page.scroll = "auto"

    def toggle_nav(e):
        page.drawer.open = not page.drawer.open
        page.update()

    def search_anime(e):
        keyword = search_input.value.lower()
        update_anime_list(keyword)

    def update_anime_list(keyword=""):
        anime_items.controls.clear()
        anime_data = get_all_anime()

        for anime in anime_data:
            if keyword and keyword not in anime[1].lower():
                continue

            anime_card = ft.Container(
                content=ft.Column(
                    [
                        ft.Image(src=anime[4] if anime[4] else "https://via.placeholder.com/200x250", width=200, height=250, fit="cover"),
                        ft.Text(anime[1], size=16, weight="bold"),
                        ft.Text(anime[2], size=12, color="grey"),
                    ],
                    alignment="center",
                    horizontal_alignment="center",
                    spacing=5
                ),
                padding=10,
                border_radius=ft.border_radius.all(10),
                ink=True,
                on_click=lambda e, a=anime: show_anime_detail(a)
            )
            anime_items.controls.append(anime_card)
        page.update()

    def show_anime_detail(anime):
        page.go(f"/detail/{anime[0]}")

    def navigate_to(route):
        def handler(e):
            page.go(route)
        return handler

    # Header
    search_input = ft.TextField(hint_text="Search anime...", width=200, on_submit=search_anime)
    profile_icon = ft.IconButton(icon=ft.Icons.ACCOUNT_CIRCLE, tooltip="Profile")

    header = ft.Row(
        [
            ft.IconButton(icon=ft.Icons.MENU, on_click=toggle_nav),
            ft.Text("OtakuZone", size=20, weight="bold"),
            search_input,
            profile_icon
        ],
        alignment="spaceBetween"
    )

    # Navigation Drawer
    page.drawer = ft.NavigationDrawer(
        controls=[
            ft.Container(ft.Text("Menu", size=18, weight="bold"), padding=10),
            ft.Container(
                ft.TextButton("🏠 Home", on_click=navigate_to("/home")),
                padding=5
            ),
            ft.Container(
                ft.TextButton("❤️ My Favorites", on_click=navigate_to("/favorites")),
                padding=5
            ),
            ft.Divider(),
            ft.Container(
                ft.TextButton("🚪 Logout", on_click=navigate_to("/login")),
                padding=5
            ),
        ]
    )

    # Anime list display
    anime_items = ft.Row(wrap=True, spacing=10, alignment="center")
    update_anime_list()

    page.add(header, ft.Divider(), anime_items)