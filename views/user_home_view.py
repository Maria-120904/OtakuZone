import flet as ft
import sqlite3
import os
from theme import set_theme, anime_card, input_field
from services.session_manager import SessionManager

DB_PATH = "database/otakuzone.db"

# Retrieve all anime
def get_all_anime():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, genre, category, image_path FROM anime")
    anime_list = cursor.fetchall()
    conn.close()
    return anime_list

def main(page: ft.Page):
    set_theme(page)
    page.title = "OtakuZone - Home"
    page.scroll = "auto"
    page.window_width = 400
    page.window_height = 700
    page.window_resizable = False

    # Initialize session
    session = SessionManager(page)
    if not session.is_logged_in():
        page.go("/")
        return

    # ✅ Custom Sidebar State
    sidebar_open = False

    def show_anime_detail(anime):
        page.go(f"/detail/{anime[0]}")

    # --- CATEGORY FILTER STATE ---
    category_names = [
        "All", "Movie", "Ongoing", "Completed",
        "Upcoming", "Popular", "TV Series", "Last update"
    ]
    selected_category = "All"

    # ✅ Fixed Anime list container (2 columns ONLY, mobile size)
    anime_items = ft.GridView(
        max_extent=180,  # 2 columns for ~360px width
        child_aspect_ratio=0.7,
        spacing=10,
        run_spacing=10,
        padding=ft.padding.symmetric(horizontal=10, vertical=8),
        width=400,  # ✅ Fixed width
        expand=True,
    )

    # Update anime list with search filter and category filter
    def update_anime_list(keyword="", selected_cat="All"):
        anime_items.controls.clear()
        anime_data = get_all_anime()
        keyword = keyword.lower()
        found = False

        for anime in anime_data:
            # Filter by search keyword
            if keyword and keyword not in anime[1].lower():
                continue

            # Filter by category
            if selected_cat != "All":
                anime_categories = [c.strip().lower() for c in (anime[3] or "").split(",")]
                if selected_cat.lower() not in anime_categories:
                    continue

            found = True
            # Show image if available, else red placeholder
            img_path = anime[4]
            if img_path and os.path.exists(img_path):
                # ✅ Image wraps to full card width
                image = ft.Container(
                    content=ft.Image(
                        src=img_path,
                        fit="cover",  # ✅ Cover fills container
                    ),
                    height=140,
                    border_radius=ft.border_radius.only(top_left=12, top_right=12),
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,  # ✅ Clip to border radius
                )
            else:
                image = ft.Container(
                    content=ft.Icon(ft.Icons.IMAGE, size=48, color="#444"),
                    height=140,
                    bgcolor="red",
                    border_radius=ft.border_radius.only(top_left=12, top_right=12),
                    alignment=ft.alignment.center,
                )

            # Title
            title = ft.Container(
                ft.Text(anime[1], size=12, weight="bold", color="white", max_lines=2, overflow="ellipsis"),
                padding=ft.padding.only(left=8, right=8, top=4, bottom=2)
            )
            
            # Genres as plain text, separated by commas
            genres = ", ".join([g.strip() for g in anime[2].split(",")])
            genre_text = ft.Container(
                ft.Text(genres, size=10, color="#b3b3b3", max_lines=2, overflow="ellipsis"),
                padding=ft.padding.only(left=8, right=8, top=2, bottom=8)  # ✅ Added bottom padding
            )
            
            # ✅ Anime container with fixed height
            card = ft.Container(
                content=ft.Column(
                    [
                        image,
                        title,
                        genre_text,
                    ],
                    spacing=0,  # ✅ No spacing between elements
                    alignment=ft.MainAxisAlignment.START,
                ),
                bgcolor="#18191A",
                border_radius=12,
                padding=0,
                on_click=lambda e, a=anime: show_anime_detail(a),
                height=220,  # ✅ Fixed card height (140 image + 80 text area)
            )
            anime_items.controls.append(card)

        if not found:
            anime_items.controls.append(
                ft.Text(f"No anime found in '{selected_cat}' category.", color="white", size=14, width=360)
            )
        page.update()

    def search_anime(e):
        update_anime_list(search_input.value, selected_category)

    def handle_logout(e):
        session.logout()
        page.go("/")

    # ✅ Custom Sidebar Overlay
    def toggle_nav(e):
        nonlocal sidebar_open
        sidebar_open = not sidebar_open
        sidebar_overlay.visible = sidebar_open
        page.update()

    def close_nav(e):
        nonlocal sidebar_open
        sidebar_open = False
        sidebar_overlay.visible = False
        page.update()

    # ✅ Sidebar Content (170px width)
    sidebar_content = ft.Container(
        content=ft.Column(
            [
                # Drawer header
                ft.Container(
                    ft.Row(
                        [
                            ft.Text("Menu", size=18, weight="bold", color="white"),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                on_click=close_nav,
                                icon_size=20,
                                icon_color="white",
                            ),
                        ],
                        alignment="spaceBetween",
                        vertical_alignment="center",
                    ),
                    padding=ft.padding.only(left=12, right=8, top=10, bottom=10),
                ),
                # Home
                ft.Container(
                    ft.GestureDetector(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.HOME, color="white", size=18),
                                ft.Text("Home", color="white", size=13, weight="bold"),
                            ],
                            alignment="start",
                            vertical_alignment="center",
                            spacing=10,
                        ),
                        on_tap=lambda e: [close_nav(e), page.go("/home")],
                        mouse_cursor="click",
                    ),
                    border_radius=8,
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                ),
                # Favorite
                ft.Container(
                    ft.GestureDetector(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.FAVORITE, color="white", size=18),
                                ft.Text("Favorite", color="white", size=13, weight="bold"),
                            ],
                            alignment="start",
                            vertical_alignment="center",
                            spacing=10,
                        ),
                        on_tap=lambda e: [close_nav(e), page.go("/favorites")],
                        mouse_cursor="click",
                    ),
                    border_radius=8,
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                ),
                # Logout
                ft.Container(
                    ft.GestureDetector(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.LOGOUT, color="white", size=18),
                                ft.Text("Logout", color="white", size=13, weight="bold"),
                            ],
                            alignment="start",
                            vertical_alignment="center",
                            spacing=10,
                        ),
                        on_tap=lambda e: [close_nav(e), handle_logout(e)],
                        mouse_cursor="click",
                    ),
                    border_radius=8,
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                ),
            ],
            spacing=5,
        ),
        width=170,  # ✅ Reduced width (180px → 170px)
        height=700,
        bgcolor="#1a1a1a",
        border=ft.border.only(right=ft.BorderSide(1, "#E50914")),
        padding=ft.padding.only(top=5),
    )

    # ✅ Sidebar Overlay (positioned relative to 400px container)
    sidebar_overlay = ft.Stack(
        [
            # Semi-transparent backdrop
            ft.GestureDetector(
                content=ft.Container(
                    bgcolor="black54",  # Semi-transparent black
                    width=400,
                    height=700,
                ),
                on_tap=close_nav,  # ✅ Close when clicking outside
            ),
            # Sidebar positioned at left
            ft.Container(
                content=sidebar_content,
                left=0,
                top=0,
            ),
        ],
        width=400,
        height=700,
        visible=False,  # Initially hidden
    )

    # ✅ Fixed Header bar with proper structure
    search_input = ft.TextField(
        hint_text="Search anime...",
        expand=True,
        on_submit=search_anime,
        text_style=ft.TextStyle(color="white"),
        cursor_color="#E50914",
        border_color="#222",
        bgcolor="#18191A",
        height=40,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=0),
    )

    header = ft.Column(
        [
            ft.Row(
                [
                    ft.IconButton(icon=ft.Icons.MENU, on_click=toggle_nav),
                    search_input,
                    ft.IconButton(icon=ft.Icons.ACCOUNT_CIRCLE, on_click=lambda e: page.go("/profile")),
                ],
                alignment="spaceBetween",
            ),
            ft.Divider(color="#E50914", height=1),  # ✅ Divider inside Column
        ],
        spacing=10,
        width=400, 
    )

    # --- CATEGORY BUTTONS ---
    category_buttons = []
    def on_category_click(e, name):
        nonlocal selected_category
        selected_category = name
        for btn in category_buttons:
            btn.bgcolor = "#E50914" if btn.data == selected_category else "black"
        update_anime_list(search_input.value, selected_category)
        page.update()

    for name in category_names:
        if name in ["Completed", "Upcoming", "TV Series"]:
            text_size = 8
        elif name == "Last update":
            text_size = 7
        else:
            text_size = 10
        btn = ft.ElevatedButton(
            content=ft.Text(name, size=text_size, color="white"),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=16),
                padding=ft.padding.symmetric(horizontal=16, vertical=0),
                bgcolor="#E50914" if name == "All" else "black",
                color="white",
            ), 
            height=36,
            data=name,
            on_click=lambda e, n=name: on_category_click(e, n),
        )
        category_buttons.append(btn)

    category_grid = ft.GridView(
        controls=category_buttons,
        max_extent=90, 
        child_aspect_ratio=2.5,
        runs_count=2,
        spacing=10,
        run_spacing=10,
        padding=ft.padding.symmetric(horizontal=10, vertical=0),
        width=400,  # ✅ Fixed width
        expand=False,
    )

    update_anime_list(selected_cat=selected_category)

    # ✅ Main layout with sidebar overlay
    main_content = ft.Column(
        [
            header,  # ✅ Header with divider inside
            ft.Container(
                category_grid, 
                margin=ft.margin.only(top=10, bottom=2),
                width=400,
            ),
            anime_items,  # ✅ Fixed 2-column grid
        ],
        width=400,  # ✅ Main container fixed width
        spacing=0,
        scroll="auto",
    )

    # ✅ Stack: Main content + Sidebar overlay
    page.add(
        ft.Stack(
            [
                main_content,
                sidebar_overlay,  # ✅ Sidebar on top
            ],
            width=400,
            height=700,
        )
    )

if __name__ == "__main__":
    ft.app(target=main)