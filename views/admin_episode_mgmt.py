import flet as ft
import sqlite3
import os
import shutil
from theme import primary_button

DB_PATH = "database/otakuzone.db"
VIDEOS_DIR = "assets/videos"

os.makedirs(VIDEOS_DIR, exist_ok=True)

# ===== DATABASE FUNCTIONS =====

def get_episodes(anime_id):
    """Get all episodes for a specific anime"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, episode_number, title, video_path, duration, upload_date
        FROM episodes
        WHERE anime_id = ?
        ORDER BY episode_number
    """, (anime_id,))
    data = cursor.fetchall()
    conn.close()
    return data

def get_next_episode_number(anime_id):
    """Get the next episode number for an anime"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(episode_number) FROM episodes WHERE anime_id = ?", (anime_id,))
    row = cursor.fetchone()
    conn.close()
    return (row[0] or 0) + 1

def episode_exists(anime_id, episode_number):
    """Check if episode already exists"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM episodes 
        WHERE anime_id = ? AND episode_number = ?
    """, (anime_id, episode_number))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def add_episode(anime_id, episode_number, title, video_path, duration=None):
    """Add new episode"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO episodes (anime_id, episode_number, title, video_path, duration)
        VALUES (?, ?, ?, ?, ?)
    """, (anime_id, episode_number, title, video_path, duration))
    conn.commit()
    conn.close()

def update_episode(episode_id, title, video_path, duration):
    """Update existing episode"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE episodes
        SET title = ?, video_path = ?, duration = ?
        WHERE id = ?
    """, (title, video_path, duration, episode_id))
    conn.commit()
    conn.close()

def delete_episode(episode_id):
    """Delete episode and its video file"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get video path before deleting
    cursor.execute("SELECT video_path FROM episodes WHERE id = ?", (episode_id,))
    row = cursor.fetchone()
    
    if row and row[0] and os.path.exists(row[0]):
        try:
            os.remove(row[0])
        except Exception as e:
            print(f"Failed to delete video file: {e}")
    
    cursor.execute("DELETE FROM episodes WHERE id = ?", (episode_id,))
    conn.commit()
    conn.close()

def get_anime_info(anime_id):
    """Get anime title and info"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM anime WHERE id = ?", (anime_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "Unknown Anime"

# ===== MAIN VIEW =====

def episode_management_view(page: ft.Page, anime_id: int):
    """Episode management page for a specific anime"""
    
    anime_title = get_anime_info(anime_id)
    
    # File picker for videos
    video_picker = ft.FilePicker()
    page.overlay.append(video_picker)
    
    selected_video = [None]
    episodes_list = ft.Column(spacing=10)
    
    def refresh_episodes():
        """Refresh the episodes list"""
        episodes_list.controls.clear()
        
        header = ft.Row(
            [
                ft.Text("Ep#", width=60, weight="bold", color="white"),
                ft.Text("Title", width=250, weight="bold", color="white"),  
                ft.Text("Duration", width=100, weight="bold", color="white"),
                ft.Text("Actions", width=120, weight="bold", color="white"),  
            ],
            alignment="start",
        )
        episodes_list.controls.append(header)
        episodes_list.controls.append(ft.Divider(color="#E50914"))
        
        episodes = get_episodes(anime_id)
        
        if not episodes:
            episodes_list.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.VIDEO_LIBRARY_OUTLINED, size=60, color="#444"),
                            ft.Text("No episodes yet", size=16, color="#b3b3b3"),
                            ft.Text("Click 'Add Episode' to create one", size=12, color="#666"),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    alignment=ft.alignment.center,
                    padding=50,
                )
            )
        else:
            for ep in episodes:
                ep_id, ep_num, ep_title, video_path, duration, upload_date = ep
                
                
                row = ft.Row(
                    [
                        ft.Text(str(ep_num), width=60, color="white", weight="bold"),
                        ft.Text(ep_title or "Untitled", width=250, color="#b3b3b3"),
                        ft.Text(duration or "N/A", width=100, color="#E50914"),
                    
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    icon_color="#E50914",
                                    icon_size=20,
                                    tooltip="Edit",
                                    on_click=lambda e, episode=ep: open_episode_form(episode)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color="red",
                                    icon_size=20,
                                    tooltip="Delete",
                                    on_click=lambda e, ep_id=ep_id, ep_num=ep_num: confirm_delete(ep_id, ep_num)
                                ),
                            ],
                            spacing=5,
                        ),
                    ],
                    alignment="start",
                )
                episodes_list.controls.append(row)
        
        page.update()
    
    def confirm_delete(ep_id, ep_num):
        """Confirm before deleting episode"""
        def delete_confirmed(e):
            delete_episode(ep_id)
            dialog.open = False
            page.update()
            refresh_episodes()
        
        def cancel_delete(e):
            dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Delete"),
            content=ft.Text(f"Are you sure you want to delete Episode {ep_num}?\n\nThis will also delete the video file."),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_delete),
                ft.ElevatedButton("Delete", bgcolor="red", color="white", on_click=delete_confirmed),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    def open_episode_form(episode=None):
        """Open add/edit episode dialog"""
        is_edit_mode = episode is not None
        
        if is_edit_mode:
            ep_id, ep_num, ep_title, video_path, duration, upload_date = episode
            selected_video[0] = video_path
        else:
            ep_num = get_next_episode_number(anime_id)
            ep_title = ""
            duration = ""
            selected_video[0] = None
        
        # Form fields
        episode_number_field = ft.TextField(
            label="Episode Number",
            value=str(ep_num),
            width=350,
            border_color="#E50914",
            disabled=is_edit_mode,  # Can't change episode number when editing
        )
        
        title_field = ft.TextField(
            label="Episode Title",
            value=ep_title or "",
            width=350,
            border_color="#E50914",
        )
        
        duration_field = ft.TextField(
            label="Duration (e.g., 24:30)",
            value=duration or "",
            width=350,
            border_color="#E50914",
        )
        
        # Video preview
        if is_edit_mode and video_path and os.path.exists(video_path):
            video_preview = ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.VIDEO_FILE, size=60, color="#E50914"),
                        ft.Text(os.path.basename(video_path), size=12, color="#b3b3b3"),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                alignment=ft.alignment.center,
                width=350,
                height=120,
                bgcolor="#18191A",
                border=ft.border.all(1, "#444"),
                border_radius=8,
            )
        else:
            video_preview = ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.VIDEO_LIBRARY, size=60, color="#444"),
                        ft.Text("No video selected", size=12, color="#b3b3b3"),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                alignment=ft.alignment.center,
                width=350,
                height=120,
                bgcolor="#18191A",
                border=ft.border.all(1, "#444"),
                border_radius=8,
            )
        
        pick_video_btn = ft.ElevatedButton(
            "Pick Video",
            icon=ft.Icons.VIDEO_FILE,
            bgcolor="#E50914",
            color="white",
            width=200,
            on_click=lambda e: video_picker.pick_files(
                allow_multiple=False,
                allowed_extensions=["mp4", "mkv", "avi", "mov"]
            ),
        )
        
        form_message = ft.Text(value="", size=12, text_align="center")
        
        def on_video_result(e: ft.FilePickerResultEvent):
            if e.files and len(e.files) > 0:
                file = e.files[0]
                selected_video[0] = file.path
                
                video_preview.content = ft.Column(
                    [
                        ft.Icon(ft.Icons.VIDEO_FILE, size=60, color="#E50914"),
                        ft.Text(os.path.basename(file.path), size=12, color="#b3b3b3"),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                )
                page.update()
        
        video_picker.on_result = on_video_result
        
        def save_episode(e):
            """Save episode (add or update)"""
            ep_number = episode_number_field.value.strip()
            ep_title = title_field.value.strip()
            ep_duration = duration_field.value.strip()
            
            if not ep_number or not ep_title or not selected_video[0]:
                form_message.value = "Episode number, title, and video are required"
                form_message.color = "red"
                page.update()
                return
            
            try:
                ep_number = int(ep_number)
            except:
                form_message.value = "Episode number must be a number"
                form_message.color = "red"
                page.update()
                return
            
            # Check if episode exists (only when adding)
            if not is_edit_mode and episode_exists(anime_id, ep_number):
                form_message.value = f"Episode {ep_number} already exists"
                form_message.color = "red"
                page.update()
                return
            
            # Save video file
            video_path = selected_video[0]
            
            # Only copy if it's a new file (not the existing one)
            if is_edit_mode and video_path == episode[3]:
                # Keep existing video path
                final_video_path = video_path
            else:
                # Create anime folder in videos directory
                anime_folder = os.path.join(VIDEOS_DIR, anime_title.lower().replace(" ", "_"))
                os.makedirs(anime_folder, exist_ok=True)
                
                # Generate filename
                ext = os.path.splitext(selected_video[0])[1].lower()
                video_filename = f"episode_{ep_number}{ext}"
                final_video_path = os.path.join(anime_folder, video_filename)
                
                # Copy video file
                try:
                    shutil.copy(selected_video[0], final_video_path)
                except Exception as ex:
                    form_message.value = f"Failed to save video: {ex}"
                    form_message.color = "red"
                    page.update()
                    return
            
            # Save to database
            if is_edit_mode:
                update_episode(ep_id, ep_title, final_video_path, ep_duration)
            else:
                add_episode(anime_id, ep_number, ep_title, final_video_path, ep_duration)
            
            dialog.open = False
            page.update()
            refresh_episodes()
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        # Create dialog
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Container(
                ft.Text(
                    f"Edit Episode {ep_num}" if is_edit_mode else "Add New Episode",
                    size=18,
                    weight="bold",
                    color="white"
                ),
                alignment=ft.alignment.center,
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        episode_number_field,
                        title_field,
                        duration_field,
                        video_preview,
                        ft.Container(pick_video_btn, alignment=ft.alignment.center),
                        form_message,
                    ],
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO,
                ),
                width=380,
                height=380,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton("Save", bgcolor="#E50914", color="white", on_click=save_episode),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    def go_back(e):
        """Navigate back to anime management"""
        page.go("/admin")
        
    header = ft.Row(
        [
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color="white",
                tooltip="Back to Anime Management",
                on_click=go_back,
            ),
            ft.Text(f"{anime_title}", size=22, weight="bold", color="white"),
        ],
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
        height=60,
    )
    
    title_and_add_row = ft.Row(
        [
            ft.Text("Manage Videos", size=16, weight="bold", color="white"),
            ft.Container(expand=True),  # Spacer
            primary_button("Add Episode", on_click=lambda e: open_episode_form(), width=150),
        ],
        alignment="spaceBetween",
        vertical_alignment="center",
    )
    
    layout = ft.Column(
        [
            ft.Container(
                header, 
                bgcolor="#18191A", 
                padding=ft.padding.symmetric(horizontal=20, vertical=10)
            ),
            title_and_add_row,
            ft.Divider(color="#E50914"),
            episodes_list,
        ],
        spacing=10,
        expand=True,
        scroll="auto",
    )
    
    refresh_episodes()
    return layout