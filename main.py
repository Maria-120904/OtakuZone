import flet as ft
from views.login_view import main as login_view
from views.signup_view import main as signup_view
from views.user_home_view import main as user_home
from views.favorites_view import main as favorites_view
from views.anime_detail_view import main as anime_detail_view
from views.admin_anime_mgmt import main as admin_anime
from views.admin_user_mgmt import main as admin_user
from views.profile_view import main as profile_view
from services.session_manager import SessionManager

# ROUTER CONTROLLER
def main(page: ft.Page):
    page.title = "OtakuZone"
    page.theme_mode = "light"
    
    session = SessionManager(page)

    def navigate(route):
        page.controls.clear()
        
        user_id = session.get_user_id()
        role = session.get_role()

        if route == "/" or route == "/login":
            login_view(page)
        elif route == "/signup":
            signup_view(page)
        elif route == "/home":
            if user_id:
                user_home(page)
            else:
                page.go("/login")
        elif route.startswith("/detail/"):
            anime_id = int(route.split("/")[-1])
            anime_detail_view(page, anime_id=anime_id)
        elif route == "/favorites":
            if user_id:
                favorites_view(page)
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
        elif route == "/profile":
            if user_id:
                profile_view(page)
            else:
                page.go("/login")
        else:
            page.add(ft.Text("404 - Page Not Found", color="red", size=20))

        page.update()

    page.on_route_change = lambda e: navigate(page.route)
    page.go("/")

if __name__ == "__main__":
    ft.app(target=main)