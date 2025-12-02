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
    page.window_width = 400
    page.window_height = 700
    page.window_resizable = False

    session = SessionManager(page)
    if not session.is_logged_in():
        page.go("/")
        return

    user_id = session.get_user_id()

    if anime_id is None:
        page.add(ft.Text("Anime not found.", color="red", width=360))
        return

    anime = get_anime_by_id(anime_id)
    if not anime:
        page.add(ft.Text("Anime not found.", color="red", width=360))
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

    # --- Description Toggle State ---
    description_expanded = False

    def toggle_description(e):
        nonlocal description_expanded
        description_expanded = not description_expanded
        # Update the icon and description visibility
        if description_expanded:
            description_icon.name = ft.Icons.KEYBOARD_ARROW_UP
            description_text.visible = True
        else:
            description_icon.name = ft.Icons.KEYBOARD_ARROW_DOWN
            description_text.visible = False
        page.update()

    header = ft.Row(
        [
            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=go_back),
            ft.Text(anime[1], size=20, weight="bold", color="white", width=320, no_wrap=True),
        ],
        alignment="start",
        vertical_alignment="center",
        width=400,
    )

    # Anime image as a red placeholder container, full width (edge to edge), 240px height, no border radius
    anime_img = ft.Container(
        width=page.window_width,
        height=240,
        bgcolor="red",
        padding=0,
        margin=0,
    )

    favorite_btn = ft.Column(
        [
            ft.IconButton(icon=ft.Icons.FAVORITE, icon_color="red" if fav_state else "white", on_click=handle_favorite),
            ft.Text("Favorite", size=12, color="white"),
        ],
        horizontal_alignment="center",
        width=100,
    )

    share_btn = ft.Column(
        [
            ft.IconButton(icon=ft.Icons.SHARE, icon_color="white"),
            ft.Text("Share", size=12, color="white"),
        ],
        horizontal_alignment="center",
        width=100,
    )

    download_btn = ft.Column(
        [
            ft.IconButton(icon=ft.Icons.DOWNLOAD, icon_color="white"),
            ft.Text("Download", size=12, color="white"),
        ],
        horizontal_alignment="center",
        width=100,
    )

    # Genre and category in one line, separated by " | "
    genres = [g.strip() for g in anime[2].split(",") if g.strip()]
    if anime[3]:
        genres.append(anime[3])
    genre_category_line = " | ".join(genres)

    # Description toggle row and text
    description_icon = ft.Icon(name=ft.Icons.KEYBOARD_ARROW_DOWN, color="white", size=18)
    description_text = ft.Text(anime[4], size=14, color="white", selectable=True, width=360, visible=False)

    description_row = ft.GestureDetector(
        content=ft.Row(
            [
                ft.Text("Description", size=14, color="white", weight="bold"),
                description_icon,
            ],
            alignment="start",
            vertical_alignment="center",
        ),
        on_tap=toggle_description,
        mouse_cursor="click",
    )

    # Episode boxes (8 per row, as many rows as needed)
    episode_boxes = []
    for i in range(anime[5]):
        episode_boxes.append(
            ft.ElevatedButton(
                content=ft.Text(str(i + 1), color="white", size=13, weight="bold"),
                style=ft.ButtonStyle(
                    bgcolor="#444444",
                    shape=ft.RoundedRectangleBorder(radius=4),
                    padding=ft.padding.symmetric(horizontal=0, vertical=0),
                ),
                width=36,
                height=36,
                disabled=True,  # Not clickable, just for display
            )
        )

    episodes_grid = ft.GridView(
        controls=episode_boxes,
        max_extent=44,  # 8 columns for ~360px width (44*8=352)
        child_aspect_ratio=1,
        spacing=8,
        run_spacing=8,
        padding=ft.padding.only(top=4, bottom=4),
        width=360,
        expand=False,
    )

    info = ft.Column(
        [
            ft.Text(genre_category_line, size=14, color="#b3b3b3", width=360),
            description_row,
            description_text,
            ft.Divider(color="#E50914"),
            ft.Text("Episodes", size=18, weight="bold", color="white", width=360),
            episodes_grid,
        ],
        spacing=6,
        width=400,
    )

    actions = ft.Row(
        [favorite_btn, share_btn, download_btn],
        alignment="spaceAround",
        width=360,
    )

    layout = ft.Column(
        [
            header,
            anime_img,
            ft.Container(actions, alignment=ft.alignment.center, padding=0, width=400),
            ft.Container(info, alignment=ft.alignment.center, padding=10, width=400),
        ],
        width=400,
        alignment="start",
        horizontal_alignment="center",
        scroll="auto",
        spacing=10,
    )

    page.add(layout)


if __name__ == "__main__":
    ft.app(target=main)