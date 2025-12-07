import flet as ft
import sqlite3
import os
from services.session_manager import SessionManager

DB_PATH = "database/otakuzone.db"

def get_favorite_anime(user_id):
    """Get favorite anime with episode count from episodes table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            a.id, 
            a.title, 
            a.genre, 
            a.category, 
            a.image_path,
            (SELECT COUNT(*) FROM episodes WHERE anime_id = a.id) as episode_count
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

    header = ft.Column(
        [
            ft.Row(
                [
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=back_to_home),
                    ft.Text("My Favorites", size=22, weight="bold", color="white"),
                ],
                alignment="start",
            ),
            ft.Divider(color="#E50914", height=1),
        ],
        spacing=10,
        width=400,
    )

    favorites = get_favorite_anime(user_id)

    if not favorites:
        page.add(
            header,
            ft.Container(
                ft.Text("No favorites yet!", size=16, italic=True, color="white"),
                padding=20,
                alignment=ft.alignment.center,
            )
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
        # Updated tuple unpacking (no episodes column, episode_count is last)
        anime_id, title, genre, category, img_path, episode_count = anime
        
        # Create image with actual anime image or red placeholder
        if img_path and os.path.exists(img_path):
            anime_image = ft.Container(
                content=ft.Image(
                    src=img_path,
                    width=80,
                    height=110,
                    fit="cover",
                ),
                width=80,
                height=110,
                border_radius=8,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                margin=ft.margin.only(right=10),
            )
        else:
            anime_image = ft.Container(
                width=80,
                height=110,
                bgcolor="red",
                border_radius=8,
                margin=ft.margin.only(right=10),
            )
        
        # Genre/category chips - ONLY FIRST 2 + "+N more"
        genre_list = [g.strip() for g in genre.split(",") if g.strip()]
        if category:
            genre_list.append(category)
        
        # Take only first 2 genres
        display_genres = genre_list[:2]
        remaining_count = len(genre_list) - 2
        
        genre_chips = [
            ft.Container(
                ft.Text(g, color="white", size=10, text_align="center"),
                bgcolor="#18191A",
                border=ft.border.all(1, "white"),
                border_radius=4,
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                margin=ft.margin.only(right=4, bottom=4),
            )
            for g in display_genres
        ]
        
        # Add "+N more" chip if there are more than 2 genres
        if remaining_count > 0:
            genre_chips.append(
                ft.Container(
                    ft.Text(f"+{remaining_count} more", color="#b3b3b3", size=9, text_align="center"),
                    bgcolor="#18191A",
                    border=ft.border.all(1, "#b3b3b3"),
                    border_radius=4,
                    padding=ft.padding.symmetric(horizontal=5, vertical=2),
                    margin=ft.margin.only(right=4, bottom=4),
                )
            )

        card = ft.GestureDetector(
            content=ft.Container(
                ft.Row(
                    [
                        anime_image,
                        ft.Column(
                            [
                                ft.Text(
                                    title, 
                                    size=14, 
                                    weight="bold", 
                                    color="white", 
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    width=270,
                                ),
                                ft.Text(
                                    f"{episode_count} episodes in total",  # Use episode_count
                                    size=11, 
                                    color="#b3b3b3",
                                    width=270,
                                ),
                                ft.Row(
                                    genre_chips, 
                                    wrap=True, 
                                    spacing=0,
                                    width=270,
                                ),
                            ],
                            alignment="start",
                            spacing=6,
                            expand=True,
                        ),
                    ],
                    alignment="start",
                    vertical_alignment="start",
                    spacing=0,
                ),
                padding=10,
                border_radius=8,
                bgcolor="#18191A",
                margin=ft.margin.only(bottom=10),
                width=380,
            ),
            on_tap=lambda e, a=anime: show_detail(a),
            mouse_cursor="click",
        )
        anime_items.controls.append(card)

    page.add(
        header,
        ft.Container(
            anime_items,
            padding=ft.padding.only(top=10),
        )
    )

if __name__ == "__main__":
    ft.app(target=main)