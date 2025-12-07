import flet as ft
import sqlite3
import os
from theme import set_theme
from services.session_manager import SessionManager

DB_PATH = "database/otakuzone.db"

def get_anime_by_id(anime_id):
    """Get anime with episode count from episodes table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            a.id, 
            a.title, 
            a.genre, 
            a.category, 
            a.description, 
            a.image_path,
            (SELECT COUNT(*) FROM episodes WHERE anime_id = a.id) as episode_count
        FROM anime a
        WHERE a.id = ?
    """, (anime_id,))
    data = cursor.fetchone()
    conn.close()
    return data

def get_episode_video(anime_id, episode_number):
    """Get video path for specific episode"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT video_path, title, duration
        FROM episodes
        WHERE anime_id = ? AND episode_number = ?
    """, (anime_id, episode_number))
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

    anime_id, title, genre, category, description, image_path, episode_count = anime

    fav_state = is_favorite(user_id, anime_id)
    
    # ✅ Track current playing episode
    current_episode = [None]
    episode_boxes = []

    def handle_favorite(e):
        nonlocal fav_state
        toggle_favorite(user_id, anime_id)
        fav_state = not fav_state
        favorite_btn.controls[0].icon_color = "red" if fav_state else "white"
        page.update()

    def go_back(e):
        page.go("/home")

    description_expanded = False

    def toggle_description(e):
        nonlocal description_expanded
        description_expanded = not description_expanded
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
            ft.Text(
                title, 
                size=20, 
                weight="bold", 
                color="white", 
                width=320, 
                overflow=ft.TextOverflow.ELLIPSIS,
                no_wrap=True
            ),
        ],
        alignment="start",
        vertical_alignment="center",
        width=400,
    )

    # ✅ Media container (image or video)
    if image_path and os.path.exists(image_path):
        initial_image = ft.Image(
            src=image_path,
            width=page.window_width,
            height=240,
            fit="cover",
        )
    else:
        initial_image = ft.Container(
            width=page.window_width,
            height=240,
            bgcolor="red",
        )

    media_container = ft.Container(
        content=initial_image,
        width=page.window_width,
        height=240,
        border_radius=6,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
    )

    # ✅ Episode title display (below video, above icons)
    episode_title_display = ft.Container(
        content=ft.Text(
            "",  # Empty by default
            size=14,
            weight="bold",
            color="white",
            text_align="left",
        ),
        alignment=ft.alignment.center_left,
        padding=ft.padding.symmetric(vertical=8, horizontal=20),
        width=360,
        visible=False,  # Hidden by default
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

    genres = [g.strip() for g in genre.split(",") if g.strip()]
    if category:
        genres.append(category)
    genre_category_line = " | ".join(genres)

    description_icon = ft.Icon(name=ft.Icons.KEYBOARD_ARROW_DOWN, color="white", size=18)
    description_text = ft.Text(description, size=14, color="white", selectable=True, width=360, visible=False)

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

    def play_episode(episode_number):
        """Load and play episode video"""
        episode_data = get_episode_video(anime_id, episode_number)
        
        if not episode_data:
            # Show error dialog
            def close_error_dialog():
                error_dialog.open = False
                page.update()
            
            error_dialog = ft.AlertDialog(
                title=ft.Text("Episode Not Available"),
                content=ft.Text(f"Episode {episode_number} video has not been uploaded yet."),
                actions=[ft.TextButton("OK", on_click=lambda e: close_error_dialog())],
            )
            
            page.overlay.append(error_dialog)
            error_dialog.open = True
            page.update()
            return
        
        video_path, ep_title, duration = episode_data
        
        if not os.path.exists(video_path):
            # Show error dialog
            def close_error_dialog():
                error_dialog.open = False
                page.update()
            
            error_dialog = ft.AlertDialog(
                title=ft.Text("Video File Missing"),
                content=ft.Text(f"Video file for Episode {episode_number} was not found on server."),
                actions=[ft.TextButton("OK", on_click=lambda e: close_error_dialog())],
            )
            
            page.overlay.append(error_dialog)
            error_dialog.open = True
            page.update()
            return
        
        # ✅ Update current episode
        current_episode[0] = episode_number
        
        # ✅ Update episode title display
        episode_title_display.content.value = f"Episode {episode_number}: {ep_title or 'Untitled'}"
        episode_title_display.visible = True
        
        # ✅ Update all episode buttons (only current one is red)
        for i, box in enumerate(episode_boxes):
            ep_num = i + 1
            if ep_num == episode_number:
                # Active episode - red background
                box.style = ft.ButtonStyle(
                    bgcolor="#E50914",
                    shape=ft.RoundedRectangleBorder(radius=4),
                    padding=ft.padding.symmetric(horizontal=0, vertical=0),
                )
            else:
                # Inactive episodes - gray with hover
                box.style = ft.ButtonStyle(
                    bgcolor={
                        ft.ControlState.DEFAULT: "#444444",
                        ft.ControlState.HOVERED: "#E50914",
                    },
                    shape=ft.RoundedRectangleBorder(radius=4),
                    padding=ft.padding.symmetric(horizontal=0, vertical=0),
                )
        
        # ✅ Create video player WITHOUT auto-play next
        video_player = ft.Video(
            playlist=[ft.VideoMedia(video_path)],
            width=page.window_width,
            height=240,
            show_controls=True,
            autoplay=True,
            # ✅ REMOVED: on_completed (no auto-play)
        )
        
        # ✅ Replace image with video
        media_container.content = video_player
        page.update()

    def handle_episode_click(episode_number):
        """Handle episode button click"""
        play_episode(episode_number)

    # ✅ Create episode buttons with PROPER lambda capture
    for i in range(episode_count):
        ep_num = i + 1
        
        # ✅ FIX: Create button with immediate value binding
        btn = ft.ElevatedButton(
            content=ft.Text(str(ep_num), color="white", size=13, weight="bold"),
            style=ft.ButtonStyle(
                bgcolor={
                    ft.ControlState.DEFAULT: "#444444",
                    ft.ControlState.HOVERED: "#E50914",
                },
                shape=ft.RoundedRectangleBorder(radius=4),
                padding=ft.padding.symmetric(horizontal=0, vertical=0),
            ),
            width=36,
            height=36,
            data=ep_num,  # ✅ Store episode number in data
        )
        
        # ✅ Use data attribute instead of closure
        btn.on_click = lambda e: handle_episode_click(e.control.data)
        
        episode_boxes.append(btn)

    episodes_grid = ft.GridView(
        controls=episode_boxes,
        max_extent=44,
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
            media_container,  # ✅ Image or video
            episode_title_display,  # ✅ Episode title (below video, above icons)
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