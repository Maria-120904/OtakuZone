import flet as ft
from theme import set_theme, primary_button, input_field
from services.email_verification_service import verify_code_and_create_account, resend_verification_code


def main(page: ft.Page, email, name):
    set_theme(page)
    page.title = "OtakuZone - Verify Email"
    page.scroll = "auto"

    # UI Components
    code_input = input_field("Enter 6-digit code")
    message_text = ft.Text(value="", size=14, text_align="center")

    # Header title
    header_title = ft.Text("Verify Email", size=20, weight="bold", color="white")

    # Subtitle
    subtitle = ft.Text(
        "A verification code has been sent to:",
        size=14,
        color="#b3b3b3",
        text_align="center"
    )

    # Email display (in red)
    email_display = ft.Text(
        email,
        size=14,
        color="#E50914",
        weight="bold",
        text_align="center"
    )

    # Back to signup
    def go_to_signup(e):
        page.go("/signup")

    # Header with back button and title
    header = ft.Container(
        content=ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=go_to_signup,
                    icon_color="white",
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            header_title,
                        ],
                        spacing=0,
                    ),
                    alignment=ft.alignment.center_left,
                ),
            ],
            spacing=0,
            alignment=ft.MainAxisAlignment.START,
        ),
        padding=ft.padding.only(left=10, right=10, top=10, bottom=20),
    )

    # Verify Code Handler
    def handle_verify_code(e):
        code = code_input.value.strip()

        # Validation
        if not code:
            message_text.value = "⚠ Please enter the verification code"
            message_text.color = "red"
            page.update()
            return

        if len(code) != 6 or not code.isdigit():
            message_text.value = "⚠ Code must be 6 digits"
            message_text.color = "red"
            page.update()
            return

        # Show verifying message
        message_text.value = "Verifying code and creating account..."
        message_text.color = "blue"
        page.update()

        # Verify code and create account
        success, msg = verify_code_and_create_account(email, code)

        if success:
            message_text.value = f"{msg} Redirecting to login..."
            message_text.color = "green"
            page.update()

            import time
            time.sleep(2)
            page.go("/login")
        else:
            message_text.value = f"{msg}"
            message_text.color = "red"
            page.update()

    # Resend Code Handler
    def handle_resend_code(e):
        message_text.value = "Resending code..."
        message_text.color = "blue"
        page.update()

        # Resend code
        success, msg = resend_verification_code(email)

        if success:
            message_text.value = f"{msg}"
            message_text.color = "green"
        else:
            message_text.value = f"{msg}"
            message_text.color = "red"

        page.update()

    # Main content container
    content_container = ft.Column(
        [
            subtitle,
            email_display,
            ft.Container(height=10),
            code_input,
            primary_button("Verify and Create Account", on_click=handle_verify_code),
            ft.TextButton(
                "Resend Code",
                on_click=handle_resend_code,
                style=ft.ButtonStyle(color="#E50914"),
            ),
            ft.Container(height=5),
            message_text,
        ],
        spacing=10,
        horizontal_alignment="center"
    )

    # Main layout
    layout = ft.Column(
        [
            header,
            ft.Container(height=20),
            content_container,
        ],
        alignment="start",
        horizontal_alignment="center",
        spacing=0,
    )

    page.add(layout)


if __name__ == "__main__":
    ft.app(target=main)