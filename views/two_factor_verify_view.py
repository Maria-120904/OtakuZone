import flet as ft
from theme import set_theme, primary_button, input_field
from services.two_factor_service import verify_2fa_code, send_2fa_code
from services.session_manager import SessionManager


def main(page: ft.Page, user_data):
    """
    user_data: dict with keys: user_id, role, email
    """
    set_theme(page)
    page.title = "OtakuZone - Two-Factor Authentication"
    page.scroll = "auto"

    session = SessionManager(page)

    # UI Components
    code_input = input_field("Enter 6-Digit Code")
    message_text = ft.Text(value="", size=14)

    # Handler for verifying 2FA code
    def handle_verify_code(e):
        code = code_input.value.strip()

        # Validation
        if not code:
            message_text.value = "Please enter the code"
            message_text.color = "red"
            page.update()
            return

        if len(code) != 6 or not code.isdigit():
            message_text.value = "Code must be 6 digits"
            message_text.color = "red"
            page.update()
            return

        # Verify code
        valid, msg = verify_2fa_code(user_data['email'], code)

        if valid:
            message_text.value = "Verification successful! Logging in..."
            message_text.color = "green"
            page.update()

            # Complete login
            session.login(user_data['user_id'], user_data['role'], user_data['email'])

            import time
            time.sleep(1)

            # Redirect based on role
            if user_data['role'] == "admin":
                page.go("/admin/anime")
            else:
                page.go("/home")
        else:
            message_text.value = f"{msg}"
            message_text.color = "red"
            page.update()

    # Handler for resending code
    def handle_resend_code(e):
        message_text.value = "Resending code..."
        message_text.color = "blue"
        page.update()

        success, msg = send_2fa_code(user_data['email'])

        if success:
            message_text.value = "New code sent to your email!"
            message_text.color = "green"
        else:
            message_text.value = f"Failed to send code: {msg}"
            message_text.color = "red"

        page.update()

    # Back to login
    def go_back(e):
        page.go("/login")

    # Layout
    layout = ft.Column(
        [
            ft.Container(
                ft.Row(
                    [
                        ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=go_back),
                        ft.Text("", expand=True),
                    ]
                ),
                padding=10,
            ),
            ft.Text("Two-Factor Authentication", size=26, weight="bold", color="white"),
            ft.Text(
                f"A verification code has been sent to: {user_data['email']}",
                size=14,
                color="#b3b3b3",
            ),
            ft.Divider(height=20, color="transparent"),
            code_input,
            primary_button("Verify Code", on_click=handle_verify_code),
            ft.Container(height=10),
            ft.TextButton(
                "Resend Code",
                on_click=handle_resend_code,
                style=ft.ButtonStyle(color="#E50914"),
            ),
            ft.Container(height=10),
            message_text,
            ft.Container(height=20),
            ft.TextButton(
                "Back to Login",
                on_click=go_back,
                style=ft.ButtonStyle(color="#E50914"),
            ),
        ],
        alignment="center",
        horizontal_alignment="center",
        spacing=10,
    )

    page.add(layout)


if __name__ == "__main__":
    ft.app(target=main)