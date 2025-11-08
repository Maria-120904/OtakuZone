import flet as ft
import sqlite3
from theme import set_theme
from services.session_manager import SessionManager

DB_PATH = "database/otakuzone.db"


def get_anime_by_id(anime_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, genre, category, description, episodes, image_path
        FROM anime WHERE id=?
    """, (anime_id,))
    data = cursor.fetchone()
    conn.close()
    return data


def is_favorite(user_id, anime_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM favorites WHERE user_id=? AND anime_id=?", (user_id, anime_id))
    fav = cursor.fetchone()
    conn.close()
    return fav is not None


def toggle_favorite(user_id, anime_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if is_favorite(user_id, anime_id):
        cursor.execute("DELETE FROM favorites WHERE user_id=? AND anime_id=?", (user_id, anime_id))
    else:
        cursor.execute("INSERT INTO favorites (user_id, anime_id) VALUES (?, ?)", (user_id, anime_id))
    conn.commit()
    conn.close()


def main(page: ft.Page, anime_id=None):
    set_theme(page)
    page.title = "OtakuZone - Anime Detail"
    page.scroll = "auto"

    session = SessionManager(page)
    if not session.is_logged_in():
        page.go("/")
        return

    user_id = session.get_user_id()

    if anime_id is None:
        page.add(ft.Text("Anime not found.", color="red"))
        return

    anime = get_anime_by_id(anime_id)
    if not anime:
        page.add(ft.Text("Anime not found.", color="red"))
        return

    fav_state = is_favorite(user_id, anime_id)

    def handle_favorite(e):
        nonlocal fav_state
        toggle_favorite(user_id, anime_id)
        fav_state = not fav_state
        favorite_btn.controls[0].icon_color = "red" if fav_state else "white"
        page.update()

    def go_back(e):
        page.go("/home")

    header = ft.Row(
        [
            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=go_back),
            ft.Text(anime[1], size=20, weight="bold", color="white"),
        ],
        alignment="start",
    )

    anime_img = ft.Image(
        src=anime[6] if anime[6] else "https://via.placeholder.com/400x200",
        width=400,
        height=200,
        fit="cover",
    )

    favorite_btn = ft.Column(
        [
            ft.IconButton(icon=ft.Icons.FAVORITE, icon_color="red" if fav_state else "white", on_click=handle_favorite),
            ft.Text("Favorite", size=12, color="white"),
        ],
        horizontal_alignment="center",
    )

    share_btn = ft.Column(
        [
            ft.IconButton(icon=ft.Icons.SHARE, icon_color="white"),
            ft.Text("Share", size=12, color="white"),
        ],
        horizontal_alignment="center",
    )

    download_btn = ft.Column(
        [
            ft.IconButton(icon=ft.Icons.DOWNLOAD, icon_color="white"),
            ft.Text("Download", size=12, color="white"),
        ],
        horizontal_alignment="center",
    )

    info = ft.Column(
        [
            ft.Text(f"Genre: {anime[2]}", size=14, color="#b3b3b3"),
            ft.Text(f"Category: {anime[3]}", size=14, color="#b3b3b3"),
            ft.Text(anime[4], size=14, color="white", selectable=True),
            ft.Divider(color="#E50914"),
            ft.Text(f"Episodes (Total {anime[5]})", size=18, weight="bold", color="white"),
            ft.Row([ft.Text(str(i + 1), size=14, color="white") for i in range(anime[5])], spacing=10, wrap=True),
        ],
        spacing=6,
    )

    actions = ft.Row([favorite_btn, share_btn, download_btn], alignment="spaceAround")

    page.add(header, anime_img, actions, info)


if __name__ == "__main__":
    ft.app(target=main)
