import flet as ft
import sqlite3
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

    def toggle_nav(e):
        page.drawer.open = not page.drawer.open
        page.update()

    def close_nav(e):
        page.drawer.open = False
        page.update()

    def show_anime_detail(anime):
        page.go(f"/detail/{anime[0]}")

    # Anime list container (2 columns, many rows)
    anime_items = ft.GridView(
        max_extent=180,  # 2 columns for 360px+padding
        child_aspect_ratio=0.7,
        spacing=10,
        run_spacing=10,
        padding=ft.padding.symmetric(horizontal=10, vertical=8),
        expand=True,
    )

    # Update anime list with search filter
    def update_anime_list(keyword=""):
        anime_items.controls.clear()
        anime_data = get_all_anime()
        keyword = keyword.lower()

        for anime in anime_data:
            if keyword and keyword not in anime[1].lower():
                continue

            # Placeholder Image (fixed width and height, no padding left/right/top, only bottom)
            image = ft.Container(
                content=ft.Icon(ft.Icons.IMAGE, size=48, color="#444"),
                width=160,
                height=140,
                bgcolor="red",
                border_radius=ft.border_radius.only(top_left=12, top_right=12),
                padding=ft.padding.only(bottom=8),
                alignment=ft.alignment.center,
            )

            # Title
            title = ft.Container(
                ft.Text(anime[1], size=12, weight="bold", color="white", max_lines=2, overflow="ellipsis"),
                padding=ft.padding.only(left=8, top=4, bottom=2)
            )
            
            # Genres as plain text, separated by commas
            genres = ", ".join([g.strip() for g in anime[2].split(",")])
            genre_text = ft.Container(
                ft.Text(genres, size=10, color="#b3b3b3", max_lines=2, overflow="ellipsis"),
                padding=ft.padding.only(left=8, top=2)
            )
            # Anime container
            card = ft.Container(
                content=ft.Column(
                    [
                        image,
                        title,
                        genre_text,
                    ],
                    spacing=2,
                    alignment=ft.MainAxisAlignment.START,
                ),
                bgcolor="#18191A",
                border_radius=12,
                padding=0,
                on_click=lambda e, a=anime: show_anime_detail(a),
            )
            anime_items.controls.append(card)
        page.update()

    def search_anime(e):
        update_anime_list(search_input.value)

    # Navigation handlers
    def navigate_to(route):
        def handler(e):
            page.go(route)
        return handler

    def handle_logout(e):
        session.logout()
        page.go("/")

    # Header bar
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

    header = ft.Row(
        [
            ft.IconButton(icon=ft.Icons.MENU, on_click=toggle_nav),
            search_input,
            ft.IconButton(icon=ft.Icons.ACCOUNT_CIRCLE, on_click=lambda e: page.go("/profile")),
        ],
        alignment="spaceBetween",
        width=400,
    )

    # Category buttons
    category_names = [
        "All", "Movie", "Ongoing", "Completed",
        "Upcoming", "Popular", "TV Series", "Last update"
    ]

    def on_category_click(e):
        # Implement filtering here if needed
        pass

    category_buttons = []
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
                bgcolor="black",
                color="white",
            ), 
            height=36,
            on_click=on_category_click,
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
        width=400,
        expand=False,
    )

    # Navigation Drawer (Sidebar)
    page.drawer = ft.NavigationDrawer(
        controls=[
            # Drawer header: Menu title and close icon
            ft.Container(
                ft.Row(
                    [
                        ft.Text("Menu", size=18, weight="bold", color="white"),
                        ft.IconButton(
                            icon=ft.Icons.MENU,
                            on_click=close_nav,
                            icon_size=24,
                            style=ft.ButtonStyle(
                                bgcolor="transparent",
                                color="white"
                            ),
                        ),
                    ],
                    alignment="spaceBetween",
                    vertical_alignment="center",
                ),
                padding=ft.padding.only(left=16, right=16, top=10, bottom=10),
                width=200,
            ),
            # Home
            ft.Container(
                ft.GestureDetector(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.HOME, color="white", size=20),
                            ft.Text("Home", color="white", size=14, weight="bold"),
                        ],
                        alignment="start",
                        vertical_alignment="center",
                    ),
                    on_tap=lambda e: [close_nav(e), page.go("/home")],
                    mouse_cursor="click",
                ),
                border_radius=8,
                padding=ft.padding.only(left=16, right=16, top=5, bottom=5),
                width=200,
            ),
            # Favorite
            ft.Container(
                ft.GestureDetector(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.FAVORITE, color="white", size=20),
                            ft.Text("Favorite", color="white", size=14, weight="bold"),
                        ],
                        alignment="start",
                        vertical_alignment="center",
                    ),
                    on_tap=lambda e: [close_nav(e), page.go("/favorites")],
                    mouse_cursor="click",
                ),
                border_radius=8,
                padding=ft.padding.only(left=16, right=16, top=5, bottom=5),
                width=200,
            ),
            # Logout
            ft.Container(
                ft.GestureDetector(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.LOGOUT, color="white", size=20),
                            ft.Text("Logout", color="white", size=14, weight="bold"),
                        ],
                        alignment="start",
                        vertical_alignment="center",
                    ),
                    on_tap=lambda e: [close_nav(e), handle_logout(e)],
                    mouse_cursor="click",
                ),
                border_radius=8,
                padding=ft.padding.only(left=16, right=16, top=5, bottom=5),
                width=200,
            ),
        ]
    )

    update_anime_list()

    page.add(
        ft.Container(header, width=400, padding=ft.padding.only(top=5, left=5, right=5)),
        ft.Divider(color="#E50914"),
        ft.Container(category_grid, margin=ft.margin.only(bottom=2)),  # 2px gap below categories
        anime_items,
    )

if __name__ == "__main__":
    ft.app(target=main)