import flet as ft

# 🎨 OtakuZone Global Theme
def set_theme(page: ft.Page):
    page.theme_mode = "dark"  # or "light"
    page.bgcolor = "#0f1115"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.padding = 20


# 🟥 Reusable primary button (Netflix style)
def primary_button(label, on_click=None, width=300):
    return ft.ElevatedButton(
        text=label,
        on_click=on_click,
        bgcolor="#E50914",  # red tone
        color="white",
        width=width,
        height=45,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            overlay_color="#ff4040",
        ),
    )


# ⌨️ Input field with consistent border and radius
def input_field(label, password=False, width=300):
    return ft.TextField(
        label=label,
        width=width,
        password=password,
        can_reveal_password=password,
        border_color="#E50914",
        border_radius=12,
        text_style=ft.TextStyle(size=14, color="white"),
        cursor_color="#E50914",
    )


# 🎞️ Anime card used in home/favorites view
def anime_card(title, genre, image, on_click=None):
    return ft.Container(
        content=ft.Column(
            [
                ft.Image(
                    src=image if image else "https://via.placeholder.com/200x250",
                    width=180,
                    height=240,
                    fit="cover",
                ),
                ft.Text(title, size=16, weight="bold", color="white"),
                ft.Text(genre, size=12, color="#b3b3b3"),
            ],
            alignment="center",
            horizontal_alignment="center",
            spacing=4,
        ),
        padding=10,
        border_radius=ft.border_radius.all(15),
        bgcolor="#1b1e23",
        ink=True,
        on_click=on_click,
        width=200,
        height=310,
    )
