import flet as ft
import sqlite3

DB_PATH = "database/otakuzone.db"

def get_favorite_anime(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.id, a.title, a.genre, a.category, a.image_path
        FROM anime a
        JOIN favorites f ON a.id = f.anime_id
        WHERE f.user_id = ?
    """, (user_id,))
    data = cursor.fetchall()
    conn.close()
    return data

def main(page: ft.Page, user_id=1):
    page.title = "OtakuZone - My Favorites"
    page.scroll = "auto"

    def back_to_home(e):
        page.go("/home")

    def show_detail(anime):
        page.go(f"/detail/{anime[0]}")

    # Header
    header = ft.Row(
        [
            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=back_to_home),
            ft.Text("My Favorites", size=22, weight="bold"),
        ],
        alignment="start",
    )

    # Fetch favorites
    favorites = get_favorite_anime(user_id)

    if not favorites:
        page.add(header, ft.Divider(), ft.Text("No favorites yet!", size=16, italic=True))
        return

    anime_items = ft.Row(wrap=True, spacing=10, alignment="center")

    for anime in favorites:
        card = ft.Container(
            content=ft.Column(
                [
                    ft.Image(
                        src=anime[4] if anime[4] else "https://via.placeholder.com/200x250",
                        width=200, height=250, fit="cover"
                    ),
                    ft.Text(anime[1], size=16, weight="bold"),
                    ft.Text(anime[2], size=12, color="grey")
                ],
                alignment="center",
                horizontal_alignment="center",
                spacing=5
            ),
            padding=10,
            border_radius=ft.border_radius.all(10),
            ink=True,
            on_click=lambda e, a=anime: show_detail(a)
        )
        anime_items.controls.append(card)

    page.add(header, ft.Divider(), anime_items)