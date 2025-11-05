import flet as ft
import sqlite3

DB_PATH = "app/database/otakuzone.db"

# --- DATABASE HELPERS ---
def get_all_anime():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, genre, category, description, episodes, image_path FROM anime")
    data = cursor.fetchall()
    conn.close()
    return data

def add_anime(title, genre, category, description, episodes, image_path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO anime (title, genre, category, description, episodes, image_path) VALUES (?, ?, ?, ?, ?, ?)",
        (title, genre, category, description, episodes, image_path)
    )
    conn.commit()
    conn.close()

def update_anime(anime_id, title, genre, category, description, episodes, image_path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE anime SET title=?, genre=?, category=?, description=?, episodes=?, image_path=? WHERE id=?",
        (title, genre, category, description, episodes, image_path, anime_id)
    )
    conn.commit()
    conn.close()

def delete_anime(anime_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM anime WHERE id=?", (anime_id,))
    conn.commit()
    conn.close()

# --- MAIN UI FUNCTION ---
def main(page: ft.Page):
    page.title = "OtakuZone - Admin Anime Management"
    page.scroll = "auto"

    anime_list_view = ft.Column(spacing=10)
    form_dialog = None

    def refresh_anime_list():
        anime_list_view.controls.clear()
        all_anime = get_all_anime()
        for a in all_anime:
            anime_row = ft.Row(
                [
                    ft.Text(a[1], width=200),
                    ft.Text(a[2], width=150),
                    ft.Text(a[3], width=120),
                    ft.Text(f"Episodes: {a[5]}", width=120),
                    ft.IconButton(icon=ft.Icons.EDIT, on_click=lambda e, anime=a: open_edit_form(anime)),
                    ft.IconButton(icon=ft.Icons.DELETE, icon_color="red", on_click=lambda e, id=a[0]: handle_delete(id))
                ],
                alignment="spaceBetween"
            )
            anime_list_view.controls.append(anime_row)
        page.update()

    def handle_delete(anime_id):
        delete_anime(anime_id)
        refresh_anime_list()

    def open_add_form(e):
        open_anime_form()

    def open_edit_form(anime):
        open_anime_form(anime)

    def open_anime_form(anime=None):
        nonlocal form_dialog
        title = ft.TextField(label="Title", value=anime[1] if anime else "")
        genre = ft.TextField(label="Genre", value=anime[2] if anime else "")
        category = ft.Dropdown(
            label="Category",
            options=[
                ft.dropdown.Option("All"),
                ft.dropdown.Option("Movie"),
                ft.dropdown.Option("Ongoing"),
                ft.dropdown.Option("Completed"),
                ft.dropdown.Option("Upcoming"),
                ft.dropdown.Option("Popular"),
                ft.dropdown.Option("Tv Series"),
                ft.dropdown.Option("Last update"),
            ],
            value=anime[3] if anime else "All",
        )
        description = ft.TextField(label="Description", multiline=True, value=anime[4] if anime else "")
        episodes = ft.TextField(label="Episodes", value=str(anime[5]) if anime else "1")
        image_path = ft.TextField(label="Image Path", value=anime[6] if anime else "")

        def pick_image_result(e: ft.FilePickerResultEvent):
            if e.files:
                image_path.value = e.files[0].path
                page.update()

        file_picker = ft.FilePicker(on_result=pick_image_result)
        page.overlay.append(file_picker)

        def save_anime(e):
            if anime:
                update_anime(anime[0], title.value, genre.value, category.value, description.value, int(episodes.value), image_path.value)
            else:
                add_anime(title.value, genre.value, category.value, description.value, int(episodes.value), image_path.value)
            form_dialog.open = False
            refresh_anime_list()

        form_content = ft.Column(
            [
                title,
                genre,
                category,
                description,
                episodes,
                ft.Row([
                    ft.Text("Image File:"),
                    ft.IconButton(icon=ft.Icons.UPLOAD_FILE, on_click=lambda _: file_picker.pick_files(allow_multiple=False)),
                    image_path
                ]),
                ft.ElevatedButton("Save", on_click=save_anime),
            ],
            width=400,
            height=500,
            scroll="auto"
        )

        form_dialog = ft.AlertDialog(title=ft.Text("Add/Edit Anime"), content=form_content)
        page.dialog = form_dialog
        form_dialog.open = True
        page.update()

    # --- HEADER ---
    header = ft.Row(
        [
            ft.Text("Admin - Anime Management", size=22, weight="bold"),
            ft.ElevatedButton("Add Anime", on_click=open_add_form)
        ],
        alignment="spaceBetween"
    )

    page.add(header, ft.Divider(), anime_list_view)
    refresh_anime_list()

if __name__ == "__main__":
    ft.app(target=main)
