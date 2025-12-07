import flet as ft
import sqlite3
import os
import shutil
from theme import primary_button
from services.session_manager import SessionManager

DB_PATH = "database/otakuzone.db"
ANIME_IMG_DIR = "assets/anime"

os.makedirs(ANIME_IMG_DIR, exist_ok=True)

GENRE_CHOICES = [
    "Action", "Supernatural", "Fantasy", "Adventure", "Sports", "Psychological",
    "Horror", "Superhero", "Romance", "Drama", "Mystery", "Historical", "Sci-Fi", "Comedy"
]
CATEGORY_CHOICES = [
    "Movie", "Ongoing", "Completed", "Upcoming", "Popular", "TV series", "Last update"
]

def get_all_anime():
    """Get all anime with episode count from episodes table"""
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
    """)
    data = cursor.fetchall()
    conn.close()
    return data

def add_anime(title, genre, category, description, image_path):
    """Add new anime with 0 episodes"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO anime (title, genre, category, description, image_path)
        VALUES (?, ?, ?, ?, ?)
    """, (title, genre, category, description, image_path))
    conn.commit()
    conn.close()

def update_anime(anime_id, title, genre, category, description, image_path):
    """Update anime (episodes managed separately)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE anime
        SET title=?, genre=?, category=?, description=?, image_path=?
        WHERE id=?
    """, (title, genre, category, description, image_path, anime_id))
    conn.commit()
    conn.close()

def delete_anime(anime_id):
    """Delete anime (episodes cascade deleted automatically)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM anime WHERE id=?", (anime_id,))
    conn.commit()
    conn.close()

def anime_management_view(page: ft.Page):
    session = SessionManager(page)
    if not session.is_logged_in() or session.get_role() != "admin":
        return ft.Text("Unauthorized", color="red")

    file_picker = getattr(page, "_anime_file_picker", None)
    if file_picker is None:
        file_picker = ft.FilePicker()
        page.overlay.append(file_picker)
        page._anime_file_picker = file_picker
    selected_image = [None]

    anime_list_view = ft.Column(spacing=10)

    def refresh_anime_list():
        anime_list_view.controls.clear()
        
        # ✅ Table header (Title, Genre, Category, Episodes, Actions)
        header_row = ft.Row(
            [
                ft.Text("Title", width=180, weight="bold", color="white"),
                ft.Text("Genre", width=150, weight="bold", color="white"),
                ft.Text("Category", width=120, weight="bold", color="white"),
                ft.Text("Episodes", width=100, weight="bold", color="white"),
                ft.Text("Actions", width=150, weight="bold", color="white"),
            ],
            alignment="start",
        )
        anime_list_view.controls.append(header_row)
        anime_list_view.controls.append(ft.Divider(color="#E50914"))
        
        animes = get_all_anime()
        if not animes:
            anime_list_view.controls.append(
                ft.Text("No anime found. Click 'Add Anime' to create one.", color="#b3b3b3", italic=True)
            )
        for a in animes:
            anime_id, title, genre, category, description, image_path, episode_count = a
            
            row = ft.Row(
                [
                    ft.Text(title, width=180, color="white"),
                    ft.Text(genre, width=150, color="#b3b3b3"),
                    ft.Text(category, width=120, color="#E50914"),
                    ft.Text(str(episode_count), width=100, color="white"),
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.MOVIE,
                                icon_color="#00ff00",
                                icon_size=20,
                                tooltip="Manage Episodes",
                                on_click=lambda e, aid=anime_id: page.go(f"/admin/episodes/{aid}")
                            ),
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_color="#E50914",
                                icon_size=20,
                                tooltip="Edit",
                                on_click=lambda e, anime=a: open_edit_form(anime)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color="red",
                                icon_size=20,
                                tooltip="Delete",
                                on_click=lambda e, aid=anime_id, t=title: confirm_delete(aid, t)
                            ),
                        ],
                        spacing=5,
                    ),
                ],
                alignment="start",
            )
            anime_list_view.controls.append(row)
        page.update()

    def confirm_delete(anime_id, anime_title):
        def delete_confirmed(e):
            delete_anime(anime_id)
            dialog.open = False
            page.update()
            refresh_anime_list()
        
        def cancel_delete(e):
            dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Delete"),
            content=ft.Text(f"Are you sure you want to delete '{anime_title}'?\n\nThis will also delete all episodes."),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_delete),
                ft.ElevatedButton("Delete", bgcolor="red", color="white", on_click=delete_confirmed),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def open_add_form(e=None):
        open_anime_form()

    def open_edit_form(anime):
        open_anime_form(anime)

    def open_anime_form(anime=None):
        is_edit_mode = anime is not None
        
        if is_edit_mode:
            anime_id, anime_title, anime_genres_str, anime_categories_str, anime_description, anime_image_path, episode_count = anime
            anime_genres = [g.strip() for g in anime_genres_str.split(",")]
            anime_categories = [c.strip() for c in anime_categories_str.split(",")]
            selected_image[0] = anime_image_path
        else:
            selected_image[0] = None
        
        title = ft.TextField(
            label="Title",
            width=350,
            border_color="#E50914",
            value=anime_title if is_edit_mode else "",
        )
        
        description = ft.TextField(
            label="Description",
            width=350,
            border_color="#E50914",
            value=anime_description if is_edit_mode else "",
        )
        
        category_checks = [
            ft.Checkbox(
                label=c, 
                value=c in anime_categories if is_edit_mode else False
            ) 
            for c in CATEGORY_CHOICES
        ]
        
        genre_checks = [
            ft.Checkbox(
                label=g, 
                value=g in anime_genres if is_edit_mode else False
            ) 
            for g in GENRE_CHOICES
        ]
        
        dropdown_expanded = [False]
        
        dropdown_button = ft.Container(
            content=ft.Row(
                [
                    ft.Text("Select Category & Genre", size=14, color="white"),
                    ft.Icon(ft.Icons.ARROW_DROP_DOWN, color="white"),
                ],
                alignment="spaceBetween",
            ),
            width=350,
            height=50,
            bgcolor="#18191A",
            border=ft.border.all(1, "#E50914"),
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=12, vertical=0),
        )
        
        dropdown_content = ft.Container(
            content=ft.Column(
                [
                    ft.Text("CATEGORY", size=12, weight="bold", color="#E50914"),
                    ft.Column(category_checks, spacing=2),
                    ft.Divider(color="#444", height=1),
                    ft.Text("GENRE", size=12, weight="bold", color="#E50914"),
                    ft.Column(genre_checks, spacing=2),
                ],
                spacing=5,
                scroll=ft.ScrollMode.AUTO,
            ),
            width=350,
            height=250,
            bgcolor="#18191A",
            border=ft.border.all(1, "#E50914"),
            border_radius=8,
            padding=10,
            visible=False,
        )
        
        def toggle_dropdown(e):
            dropdown_expanded[0] = not dropdown_expanded[0]
            dropdown_content.visible = dropdown_expanded[0]
            dropdown_button.content.controls[1].name = (
                ft.Icons.ARROW_DROP_UP if dropdown_expanded[0] else ft.Icons.ARROW_DROP_DOWN
            )
            page.update()
        
        dropdown_clickable = ft.GestureDetector(
            content=dropdown_button,
            on_tap=toggle_dropdown,
            mouse_cursor="click",
        )
        
        if is_edit_mode and anime_image_path and os.path.exists(anime_image_path):
            image_preview = ft.Container(
                content=ft.Stack(
                    [
                        ft.Container(
                            content=ft.Image(
                                src=anime_image_path,
                                fit=ft.ImageFit.COVER,
                            ),
                            width=350,
                            height=180,
                            border_radius=8,
                            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                        ),
                    ],
                ),
                width=350,
                height=180,
                bgcolor="#18191A",
                border=ft.border.all(1, "#444"),
                border_radius=8,
            )
        else:
            image_preview = ft.Container(
                content=ft.Stack(
                    [
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Icon(ft.Icons.IMAGE, size=60, color="#444"),
                                    ft.Text("No image selected", size=12, color="#b3b3b3"),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=8,
                            ),
                            alignment=ft.alignment.center,
                            width=350,
                            height=180,
                        ),
                    ],
                ),
                width=350,
                height=180,
                bgcolor="#18191A",
                border=ft.border.all(1, "#444"),
                border_radius=8,
            )
        
        pick_btn = ft.ElevatedButton(
            "Pick Image",
            icon=ft.Icons.IMAGE,
            bgcolor="#E50914",
            color="white",
            width=200,
            on_click=lambda e: file_picker.pick_files(
                allow_multiple=False,
                allowed_extensions=["jpg", "jpeg", "png"]
            ),
        )
        
        form_message = ft.Text(value="", size=12, text_align="center")

        def on_file_result(e: ft.FilePickerResultEvent):
            if e.files and len(e.files) > 0:
                file = e.files[0]
                selected_image[0] = file.path
                
                image_preview.content = ft.Stack(
                    [
                        ft.Container(
                            content=ft.Image(
                                src=file.path,
                                fit=ft.ImageFit.COVER,
                            ),
                            width=350,
                            height=180,
                            border_radius=8,
                            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                        ),
                    ],
                )
                page.update()
        
        file_picker.on_result = on_file_result

        def save_anime(e):
            t = title.value.strip()
            genres = [cb.label for cb in genre_checks if cb.value]
            categories = [cb.label for cb in category_checks if cb.value]
            desc = description.value.strip()
            
            if not t or not genres or not categories or not selected_image[0]:
                form_message.value = "❌ All fields and image are required"
                form_message.color = "red"
                page.update()
                return

            if is_edit_mode:
                img_path = selected_image[0]
                
                if selected_image[0] != anime_image_path:
                    ext = os.path.splitext(selected_image[0])[1].lower()
                    safe_title = t.lower().replace(" ", "_")
                    img_filename = f"{safe_title}{ext}"
                    img_path = os.path.join(ANIME_IMG_DIR, img_filename)
                    
                    try:
                        shutil.copy(selected_image[0], img_path)
                    except Exception as ex:
                        form_message.value = f"❌ Failed to save image: {ex}"
                        form_message.color = "red"
                        page.update()
                        return
                
                update_anime(anime_id, t, ", ".join(genres), ", ".join(categories), desc, img_path)
            
            else:
                ext = os.path.splitext(selected_image[0])[1].lower()
                safe_title = t.lower().replace(" ", "_")
                img_filename = f"{safe_title}{ext}"
                img_path = os.path.join(ANIME_IMG_DIR, img_filename)
                
                try:
                    shutil.copy(selected_image[0], img_path)
                except Exception as ex:
                    form_message.value = f"❌ Failed to save image: {ex}"
                    form_message.color = "red"
                    page.update()
                    return

                add_anime(t, ", ".join(genres), ", ".join(categories), desc, img_path)
            
            dialog.open = False
            page.update()
            refresh_anime_list()

        def close_dialog(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Container(
                ft.Text(
                    "Edit Anime" if is_edit_mode else "Add New Anime",
                    size=18, 
                    weight="bold", 
                    color="white"
                ),
                alignment=ft.alignment.center,
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        title,
                        description,
                        dropdown_clickable,
                        dropdown_content,
                        image_preview,
                        ft.Container(pick_btn, alignment=ft.alignment.center),
                        form_message,
                    ],
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO,
                ),
                width=380,
                height=420,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton("Save", bgcolor="#E50914", color="white", on_click=save_anime),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # ✅ Title and Add Anime button in one row (ABOVE the table)
    title_and_add_row = ft.Row(
        [
            ft.Text("Manage Anime", size=16, weight="bold", color="white"),
            ft.Container(expand=True),  # Spacer
            primary_button("Add Anime", open_add_form, width=150),
        ],
        alignment="spaceBetween",
        vertical_alignment="center",
    )

    layout = ft.Column(
        [
            title_and_add_row,  # ✅ Title + Add button (above divider)
            ft.Divider(color="#E50914", height=1),  # ✅ Divider below title/button
            anime_list_view,  # ✅ Table headers and data
        ],
        spacing=10,
        expand=True,
        scroll="auto"
    )

    refresh_anime_list()
    return layout