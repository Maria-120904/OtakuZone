import flet as ft
import sqlite3
from services.session_manager import SessionManager

DB_PATH = "database/otakuzone.db"

def get_favorite_anime(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.id, a.title, a.genre, a.category, a.episodes
        FROM anime a
        JOIN favorites f ON a.id = f.anime_id
        WHERE f.user_id = ?
    """, (user_id,))
    data = cursor.fetchall()
    conn.close()
    return data

def main(page: ft.Page):
    page.title = "OtakuZone - My Favorites"
    page.scroll = "auto"
    page.window_width = 400
    page.window_height = 700
    page.window_resizable = False

    session = SessionManager(page)
    if not session.is_logged_in():
        page.go("/login")
        return
    
    user_id = session.get_user_id()

    def back_to_home(e):
        page.go("/home")

    def show_detail(anime):
        page.go(f"/detail/{anime[0]}")

    # Header
    header = ft.Row(
        [
            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=back_to_home),
            ft.Text("My Favorites", size=22, weight="bold", color="white"),
        ],
        alignment="start",
        width=400,
    )

    favorites = get_favorite_anime(user_id)

    if not favorites:
        page.add(
            header,
            ft.Divider(color="#E50914"),
            ft.Text("No favorites yet!", size=16, italic=True, color="white", width=360)
        )
        return

    anime_items = ft.Column(
        alignment="center",
        horizontal_alignment="center",
        spacing=10,
        width=400,
        scroll="auto"
    )

    for anime in favorites:
        # genre/category chips
        genre_list = [g.strip() for g in anime[2].split(",") if g.strip()]
        if anime[3]:
            genre_list.append(anime[3])
        genre_chips = [
            ft.Container(
                ft.Text(g, color="white", size=11, text_align="center"),
                bgcolor="#18191A",
                border=ft.border.all(1, "white"),
                border_radius=4,
                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                margin=ft.margin.only(right=4, top=2, bottom=2),
            )
            for g in genre_list
        ]

        card = ft.GestureDetector(
            content=ft.Container(
                ft.Row(
                    [
                        # Red image placeholder
                        ft.Container(
                            width=80,
                            height=110,
                            bgcolor="red",
                            border_radius=4,
                            margin=ft.margin.only(right=2),
                        ),
                        # Info
                        ft.Column(
                            [
                                ft.Text(anime[1], size=15, weight="bold", color="white", max_lines=2, overflow="ellipsis"),
                                ft.Text(f"{anime[4]} episodes in total", size=12, color="#cccccc"),
                                ft.Row(genre_chips, wrap=True, spacing=0),
                            ],
                            alignment="start",
                            spacing=4,
                            width=220,
                        ),
                    ],
                    alignment="start",
                    vertical_alignment="center",
                ),
                padding=10,
                border_radius=8,
                bgcolor="#18191A",
                margin=ft.margin.only(bottom=10),
                height=130,
                width=380,
            ),
            on_tap=lambda e, a=anime: show_detail(a),
            mouse_cursor="click",
        )
        anime_items.controls.append(card)

    page.add(
        header,
        ft.Divider(color="#E50914"),
        anime_items
    )

if __name__ == "__main__":
    ft.app(target=main)