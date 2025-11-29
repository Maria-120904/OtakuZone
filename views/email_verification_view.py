import flet as ft
from theme import set_theme, primary_button, input_field
from services.email_verification_service import verify_code_and_create_account, resend_verification_code


def main(page: ft.Page, email, name):
    set_theme(page)
    page.title = "OtakuZone - Verify Email"
    page.scroll = "auto"

    # UI Components
    code_input = input_field("Enter 6-Digit Verification Code")
    message_text = ft.Text(value="", size=14)

    # Handler for verifying code
    def handle_verify_code(e):
        code = code_input.value.strip()

        # Validation
        if not code:
            message_text.value = "Please enter the verification code"
            message_text.color = "red"
            page.update()
            return

        if len(code) != 6 or not code.isdigit():
            message_text.value = "Code must be 6 digits"
            message_text.color = "red"
            page.update()
            return

        # Verify code and create account
        success, msg = verify_code_and_create_account(email, code)

        if success:
            message_text.value = "Account created successfully! Redirecting to login..."
            message_text.color = "green"
            page.update()

            import time
            time.sleep(2)
            page.go("/login")
        else:
            message_text.value = f"{msg}"
            message_text.color = "red"
            page.update()

    # Handler for resending code
    def handle_resend_code(e):
        message_text.value = "Resending verification code..."
        message_text.color = "blue"
        page.update()

        success, msg = resend_verification_code(email)

        if success:
            message_text.value = "New verification code sent to your email!"
            message_text.color = "green"
        else:
            message_text.value = f"{msg}"
            message_text.color = "red"

        page.update()

    # Back to signup
    def go_back(e):
        page.go("/signup")

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
            ft.Text("Verify Your Email", size=26, weight="bold", color="white"),
            ft.Text(
                f"Hi {name}!",
                size=16,
                color="white",
                weight="bold",
            ),
            ft.Text(
                f"A verification code has been sent to:",
                size=14,
                color="#b3b3b3",
            ),
            ft.Text(
                email,
                size=14,
                color="#E50914",
                weight="bold",
            ),
            ft.Text(
                "Please enter the 6-digit code to complete your registration.",
                size=14,
                color="#b3b3b3",
            ),
            ft.Divider(height=20, color="transparent"),
            code_input,
            primary_button("Verify and Create Account", on_click=handle_verify_code),
            ft.Container(height=10),
            ft.TextButton(
                "Resend Verification Code",
                on_click=handle_resend_code,
                style=ft.ButtonStyle(color="#E50914"),
            ),
            ft.Container(height=10),
            message_text,
            ft.Container(height=20),
            ft.TextButton(
                "Back to Sign Up",
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