import flet as ft
import sqlite3

DB_PATH = "app/database/otakuzone.db"

def get_anime_by_id(anime_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, genre, category, description, episodes, image_path FROM anime WHERE id=?", (anime_id,))
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

def main(page: ft.Page, anime_id=1, user_id=1):
    page.title = "OtakuZone - Anime Detail"
    page.scroll = "auto"

    anime = get_anime_by_id(anime_id)
    if not anime:
        page.add(ft.Text("Anime not found."))
        return

    fav_state = is_favorite(user_id, anime_id)

    # Handlers
    def handle_favorite(e):
        nonlocal fav_state
        toggle_favorite(user_id, anime_id)
        fav_state = not fav_state
        favorite_btn.icon_color = "red" if fav_state else "black"
        page.update()

    # Header
    header = ft.Row(
        [
            ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda e: page.window_close()),  # placeholder back
            ft.Text(anime[1], size=20, weight="bold"),
        ],
        alignment="start"
    )

    # Anime image
    anime_img = ft.Image(
        src=anime[6] if anime[6] else "https://via.placeholder.com/400x200",
        width=400,
        height=200,
        fit="cover",
    )

    # Action icons
    favorite_btn = ft.Column(
        [ft.IconButton(icon=ft.icons.FAVORITE, icon_color="red" if fav_state else "black", on_click=handle_favorite),
         ft.Text("Favorite", size=12)],
        horizontal_alignment="center"
    )
    share_btn = ft.Column(
        [ft.IconButton(icon=ft.icons.SHARE, icon_color="black"),
         ft.Text("Share", size=12)],
        horizontal_alignment="center"
    )
    download_btn = ft.Column(
        [ft.IconButton(icon=ft.icons.DOWNLOAD, icon_color="black"),
         ft.Text("Download", size=12)],
        horizontal_alignment="center"
    )

    # Info
    info = ft.Column(
        [
            ft.Text(f"Genre: {anime[2]}", size=14, color="grey"),
            ft.Text(f"Category: {anime[3]}", size=14, color="grey"),
            ft.Text(anime[4], size=14, selectable=True),
            ft.Divider(),
            ft.Text(f"Episodes  (Total {anime[5]})", size=18, weight="bold"),
            ft.Row([ft.Text(str(i+1), size=14) for i in range(anime[5])], spacing=10),
        ],
        spacing=5
    )

    actions = ft.Row([favorite_btn, share_btn, download_btn], alignment="spaceAround")

    page.add(header, anime_img, actions, info)

if __name__ == "__main__":
    ft.app(target=main)
