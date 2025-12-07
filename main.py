import flet as ft
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

from views.login_view import main as login_view
from views.signup_view import main as signup_view
from views.user_home_view import main as user_home
from views.favorites_view import main as favorites_view
from views.anime_detail_view import main as anime_detail_view
from views.admin_view import main as admin_view 
from views.profile_view import main as profile_view
from views.forgot_password_view import main as forgot_password_view
from views.two_factor_verify_view import main as two_factor_verify_view
from views.email_verification_view import main as email_verification_view
from views.admin_episode_mgmt import episode_management_view
from services.session_manager import SessionManager

# ROUTER CONTROLLER
def main(page: ft.Page):
    page.title = "OtakuZone"
    page.theme_mode = "light"
    page.window.width = 400
    page.window.height = 700
    page.window.resizable = False
    
    session = SessionManager(page)

    def navigate(route):
        user_id = session.get_user_id()
        role = session.get_role()

        if route == "/admin" or route.startswith("/admin/"):
            if role == "admin":
                page.window.width = 1920
                page.window.height = 1080
                page.window.resizable = True
                page.window.maximized = True
                page.update()
        elif route == "/profile":
            if role == "admin":
                # Keep desktop size for admin
                page.window.width = 1920
                page.window.height = 1080
                page.window.resizable = True
                page.window.maximized = True
            else:
                # Mobile size for regular users
                page.window.width = 400
                page.window.height = 700
                page.window.resizable = False
                page.window.maximized = False
            page.update()
        elif route in ["/home", "/favorites"] or route.startswith("/detail/"):
            if role != "admin":
                page.window.width = 400
                page.window.height = 700
                page.window.resizable = False
                page.window.maximized = False
                page.update()
        elif route in ["/", "/login", "/signup", "/forgot-password", "/2fa-verify", "/verify-email"]:
            page.window.maximized = False
            page.window.full_screen = False
            page.update()
            
            # Small delay to ensure un-maximize completes
            import time
            time.sleep(0.05)
            
            page.window.width = 400
            page.window.height = 700
            page.window.resizable = True  # Allow manual resizing
            page.update()

        # Clear page controls BEFORE navigating (except overlays)
        page.controls.clear()

        if route == "/" or route == "/login":
            login_view(page)
        elif route == "/signup":
            signup_view(page)
        elif route == "/forgot-password":
            forgot_password_view(page)
        elif route == "/2fa-verify":
            user_data = page.session.get("2fa_user_data")
            if user_data:
                two_factor_verify_view(page)
            else:
                page.go("/login")
        elif route == "/verify-email":
            email = page.session.get("verification_email")
            name = page.session.get("verification_name")
            if email and name:
                email_verification_view(page, email, name)
            else:
                page.go("/signup")
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
        elif route == "/admin":
            if role == "admin":
                admin_view(page)
            else:
                page.go("/login")
        elif route.startswith("/admin/episodes/"):
            if role == "admin":
                anime_id = int(route.split("/")[-1])
                page.add(episode_management_view(page, anime_id))
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
    ft.app(target=main, view=ft.AppView.FLET_APP)