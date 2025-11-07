import flet as ft
from views.login_view import main as login_view
from views.signup_view import main as signup_view
from views.user_home_view import main as user_home
from views.favorites_view import main as favorites_view
from views.anime_detail_view import main as anime_detail_view
from views.admin_anime_mgmt import main as admin_anime
from views.admin_user_mgmt import main as admin_user


# ROUTER CONTROLLER
def main(page: ft.Page):
    page.title = "OtakuZone"
    page.theme_mode = "light"

    # Initialize session storage
    if not hasattr(page, 'session_data'):
        page.session_data = {"user_id": None, "role": None, "username": None}

    def navigate(route):
        page.controls.clear()
        
        user_id = page.session_data.get("user_id")
        role = page.session_data.get("role")

        if route == "/" or route == "/login":
            login_view(page)
        elif route == "/signup":
            signup_view(page)
        elif route == "/home":
            if user_id:
                user_home(page, user_id=user_id)
            else:
                page.go("/login")
        elif route.startswith("/detail/"):
            anime_id = int(route.split("/")[-1])
            anime_detail_view(page, anime_id=anime_id, user_id=user_id or 1)
        elif route == "/favorites":
            if user_id:
                favorites_view(page, user_id=user_id)
            else:
                page.go("/login")
        elif route == "/admin/anime":
            if role == "admin":
                admin_anime(page)
            else:
                page.go("/login")
        elif route == "/admin/users":
            if role == "admin":
                admin_user(page)
            else:
                page.go("/login")
        else:
            page.add(ft.Text("404 - Page Not Found", color="red", size=20))

        page.update()

    page.on_route_change = lambda e: navigate(page.route)
    page.go("/")

if __name__ == "__main__":
    ft.app(target=main)