import flet as ft

class SessionManager:
    def __init__(self, page: ft.Page):
        self.page = page
        if self.page.session.get("user_id") is None:
            self.page.session.set("user_id", None)
            self.page.session.set("role", None)
            self.page.session.set("email", None)

    def login(self, user_id, role, email):
        self.page.session.set("user_id", user_id)
        self.page.session.set("role", role)
        self.page.session.set("email", email)

    def logout(self):
        self.page.session.set("user_id", None)
        self.page.session.set("role", None)
        self.page.session.set("email", None)

    def is_logged_in(self):
        return self.page.session.get("user_id") is not None

    def get_role(self):
        return self.page.session.get("role")

    def get_user_id(self):
        return self.page.session.get("user_id")