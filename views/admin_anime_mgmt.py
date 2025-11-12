import flet as ft
import sqlite3
from theme import set_theme, primary_button
from services.session_manager import SessionManager

DB_PATH = "database/otakuzone.db"


def get_all_anime():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, genre, category, description, episodes, image_path
        FROM anime
    """)
    data = cursor.fetchall()
    conn.close()
    return data


def add_anime(title, genre, category, description, episodes, image_path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO anime (title, genre, category, description, episodes, image_path)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, genre, category, description, episodes, image_path))
    conn.commit()
    conn.close()


def update_anime(anime_id, title, genre, category, description, episodes, image_path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE anime
        SET title=?, genre=?, category=?, description=?, episodes=?, image_path=?
        WHERE id=?
    """, (title, genre, category, description, episodes, image_path, anime_id))
    conn.commit()
    conn.close()


def delete_anime(anime_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM anime WHERE id=?", (anime_id,))
    conn.commit()
    conn.close()


def main(page: ft.Page):
    set_theme(page)
    page.title = "OtakuZone - Admin Anime Management"
    page.scroll = "auto"

    session = SessionManager(page)
    if not session.is_logged_in() or session.get_role() != "admin":
        page.go("/")
        return

    anime_list_view = ft.Column(spacing=10)
    form_dialog = None
    message_text = ft.Text(value="", size=14)

    def refresh_anime_list():
        anime_list_view.controls.clear()
        
        # Add header row
        header_row = ft.Row(
            [
                ft.Text("Title", width=180, weight="bold", color="white"),
                ft.Text("Genre", width=150, weight="bold", color="white"),
                ft.Text("Category", width=120, weight="bold", color="white"),
                ft.Text("Episodes", width=100, weight="bold", color="white"),
                ft.Text("Actions", width=120, weight="bold", color="white"),
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
            row = ft.Row(
                [
                    ft.Text(a[1], width=180, color="white"),
                    ft.Text(a[2], width=150, color="#b3b3b3"),
                    ft.Text(a[3], width=120, color="#E50914"),
                    ft.Text(str(a[5]), width=100, color="white"),
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_color="#E50914",
                                tooltip="Edit",
                                on_click=lambda e, anime=a: open_edit_form(anime)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color="red",
                                tooltip="Delete",
                                on_click=lambda e, anime_id=a[0], title=a[1]: confirm_delete(anime_id, title)
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
            message_text.value = f"✅ '{anime_title}' deleted successfully"
            message_text.color = "green"
            dialog.open = False
            refresh_anime_list()
        
        def cancel_delete(e):
            dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text(f"Are you sure you want to delete '{anime_title}'?"),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_delete),
                ft.ElevatedButton("Delete", bgcolor="red", color="white", on_click=delete_confirmed),
            ],
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()

    def open_add_form(e):
        open_anime_form()

    def open_edit_form(anime):
        open_anime_form(anime)

    def open_anime_form(anime=None):
        nonlocal form_dialog
        
        title = ft.TextField(
            label="Title",
            value=anime[1] if anime else "",
            width=350,
            border_color="#E50914"
        )
        genre = ft.TextField(
            label="Genre",
            value=anime[2] if anime else "",
            width=350,
            border_color="#E50914"
        )
        category = ft.Dropdown(
            label="Category",
            options=[
                ft.dropdown.Option("All"),
                ft.dropdown.Option("Movie"),
                ft.dropdown.Option("Ongoing"),
                ft.dropdown.Option("Completed"),
                ft.dropdown.Option("Upcoming"),
                ft.dropdown.Option("Popular"),
                ft.dropdown.Option("TV Series"),
                ft.dropdown.Option("Last Update")
            ],
            value=anime[3] if anime else "All",
            width=350,
            border_color="#E50914"
        )
        description = ft.TextField(
            label="Description",
            multiline=True,
            value=anime[4] if anime else "",
            width=350,
            min_lines=3,
            max_lines=5,
            border_color="#E50914"
        )
        episodes = ft.TextField(
            label="Episodes",
            value=str(anime[5]) if anime else "1",
            width=350,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color="#E50914"
        )
        image_path = ft.TextField(
            label="Image Path/URL",
            value=anime[6] if anime else "",
            width=350,
            border_color="#E50914"
        )
        
        form_message = ft.Text(value="", size=12)

        def pick_image_result(e: ft.FilePickerResultEvent):
            if e.files:
                image_path.value = e.files[0].path
                page.update()

        file_picker = ft.FilePicker(on_result=pick_image_result)
        page.overlay.append(file_picker)

        def save_anime(e):
            # Validation
            if not title.value or not genre.value:
                form_message.value = "❌ Title and Genre are required"
                form_message.color = "red"
                page.update()
                return
            
            try:
                ep_count = int(episodes.value) if episodes.value else 0
            except ValueError:
                form_message.value = "❌ Episodes must be a number"
                form_message.color = "red"
                page.update()
                return
            
            if anime:
                update_anime(
                    anime[0],
                    title.value,
                    genre.value,
                    category.value,
                    description.value,
                    ep_count,
                    image_path.value
                )
                message_text.value = f"✅ '{title.value}' updated successfully"
            else:
                add_anime(
                    title.value,
                    genre.value,
                    category.value,
                    description.value,
                    ep_count,
                    image_path.value
                )
                message_text.value = f"✅ '{title.value}' added successfully"
            
            message_text.color = "green"
            form_dialog.open = False
            refresh_anime_list()
        
        def cancel_form(e):
            form_dialog.open = False
            page.update()

        form_content = ft.Column(
            [
                title,
                genre,
                category,
                description,
                episodes,
                ft.Row(
                    [
                        image_path,
                        ft.IconButton(
                            icon=ft.Icons.UPLOAD_FILE,
                            tooltip="Upload Image",
                            on_click=lambda _: file_picker.pick_files(
                                allow_multiple=False,
                                file_type=ft.FilePickerFileType.IMAGE
                            )
                        ),
                    ],
                    spacing=5,
                ),
                form_message,
            ],
            width=400,
            height=450,
            scroll="auto",
            spacing=10,
        )

        form_dialog = ft.AlertDialog(
            title=ft.Text("Edit Anime" if anime else "Add New Anime"),
            content=form_content,
            actions=[
                ft.TextButton("Cancel", on_click=cancel_form),
                ft.ElevatedButton(
                    "Save",
                    bgcolor="#E50914",
                    color="white",
                    on_click=save_anime
                ),
            ],
        )
        
        page.dialog = form_dialog
        form_dialog.open = True
        page.update()

    # Navigation
    def go_to_user_management(e):
        page.go("/admin/users")
    
    def logout(e):
        session.logout()
        page.go("/")

    # Header
    header = ft.Row(
        [
            ft.Text("Admin - Anime Management", size=22, weight="bold", color="white"),
            ft.Row(
                [
                    primary_button("User Management", go_to_user_management, width=180),
                    primary_button("Add Anime", open_add_form, width=150),
                    ft.IconButton(
                        icon=ft.Icons.LOGOUT,
                        icon_color="red",
                        tooltip="Logout",
                        on_click=logout
                    ),
                ],
                spacing=10
            ),
        ],
        alignment="spaceBetween",
    )

    page.add(
        header,
        ft.Divider(color="#E50914"),
        message_text,
        ft.Divider(height=10, color="transparent"),
        anime_list_view
    )
    
    refresh_anime_list()


if __name__ == "__main__":
    ft.app(target=main)