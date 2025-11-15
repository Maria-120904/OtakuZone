import flet as ft
import re
from theme import set_theme, primary_button, input_field
from services.password_reset_service import send_reset_code, verify_reset_code, reset_password


def main(page: ft.Page):
    set_theme(page)
    page.title = "OtakuZone - Forgot Password"
    page.scroll = "auto"

    # State management
    current_step = {"value": 1}  # 1: Email, 2: Code, 3: New Password
    user_email = {"value": ""}

    # UI Components
    email_input = input_field("Email")
    code_input = input_field("Verification Code")
    new_password_input = input_field("New Password", password=True)
    confirm_password_input = input_field("Confirm Password", password=True)
    message_text = ft.Text(value="", size=14)

    # Containers for different steps
    step1_container = ft.Column(visible=True, spacing=10)
    step2_container = ft.Column(visible=False, spacing=10)
    step3_container = ft.Column(visible=False, spacing=10)

    # Step 1: Request Reset Code
    def handle_send_code(e):
        email = email_input.value.strip()

        # Validation
        if not email:
            message_text.value = "⚠ Please enter your email"
            message_text.color = "red"
            page.update()
            return

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            message_text.value = "⚠ Invalid email format"
            message_text.color = "red"
            page.update()
            return

        # Show loading
        message_text.value = "Sending reset code..."
        message_text.color = "blue"
        page.update()

        # Send code
        success, msg = send_reset_code(email)

        if success:
            user_email["value"] = email
            message_text.value = f"{msg}"
            message_text.color = "green"
            
            # Move to step 2
            current_step["value"] = 2
            step1_container.visible = False
            step2_container.visible = True
        else:
            message_text.value = f"{msg}"
            message_text.color = "red"

        page.update()

    # Step 2: Verify Code
    def handle_verify_code(e):
        code = code_input.value.strip()

        if not code:
            message_text.value = "⚠ Please enter the code"
            message_text.color = "red"
            page.update()
            return

        if len(code) != 6 or not code.isdigit():
            message_text.value = "⚠ Code must be 6 digits"
            message_text.color = "red"
            page.update()
            return

        # Verify code
        valid, msg = verify_reset_code(user_email["value"], code)

        if valid:
            message_text.value = f"{msg}"
            message_text.color = "green"
            
            # Move to step 3
            current_step["value"] = 3
            step2_container.visible = False
            step3_container.visible = True
        else:
            message_text.value = f"{msg}"
            message_text.color = "red"

        page.update()

    # Step 3: Reset Password
    def handle_reset_password(e):
        new_pw = new_password_input.value.strip()
        confirm_pw = confirm_password_input.value.strip()
        code = code_input.value.strip()

        # Validation
        if not new_pw or not confirm_pw:
            message_text.value = "⚠ Please fill in all fields"
            message_text.color = "red"
            page.update()
            return

        if new_pw != confirm_pw:
            message_text.value = "Passwords do not match"
            message_text.color = "red"
            page.update()
            return

        if len(new_pw) < 6:
            message_text.value = "Password must be at least 6 characters"
            message_text.color = "red"
            page.update()
            return

        # Reset password
        success, msg = reset_password(user_email["value"], code, new_pw)

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

    # Resend Code
    def handle_resend_code(e):
        message_text.value = "Resending code..."
        message_text.color = "blue"
        page.update()

        success, msg = send_reset_code(user_email["value"])
        
        if success:
            message_text.value = f"{msg}"
            message_text.color = "green"
        else:
            message_text.value = f"{msg}"
            message_text.color = "red"

        page.update()

    # Back to login
    def go_to_login(e):
        page.go("/login")

    # Build Step 1 Container
    step1_container.controls = [
        ft.Text("Reset Password", size=26, weight="bold", color="white"),
        ft.Text("Enter your email to receive a reset code", size=14, color="#b3b3b3"),
        ft.Divider(height=20, color="transparent"),
        email_input,
        primary_button("Send Reset Code", on_click=handle_send_code),
    ]

    # Build Step 2 Container
    step2_container.controls = [
        ft.Text("Verify Code", size=26, weight="bold", color="white"),
        ft.Text(f"Code sent to: {user_email.get('value', '')}", size=14, color="#b3b3b3"),
        ft.Divider(height=20, color="transparent"),
        code_input,
        primary_button("Verify Code", on_click=handle_verify_code),
        ft.TextButton(
            "Resend Code",
            on_click=handle_resend_code,
            style=ft.ButtonStyle(color="#E50914"),
        ),
    ]

    # Build Step 3 Container
    step3_container.controls = [
        ft.Text("Set New Password", size=26, weight="bold", color="white"),
        ft.Text("Enter your new password", size=14, color="#b3b3b3"),
        ft.Divider(height=20, color="transparent"),
        new_password_input,
        confirm_password_input,
        primary_button("Reset Password", on_click=handle_reset_password),
    ]

    # Main layout
    layout = ft.Column(
        [
            ft.Container(
                ft.Row(
                    [
                        ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=go_to_login),
                        ft.Text("", expand=True),
                    ]
                ),
                padding=10,
            ),
            step1_container,
            step2_container,
            step3_container,
            ft.Container(height=10),
            message_text,
            ft.Container(height=20),
            ft.TextButton(
                "Back to Login",
                on_click=go_to_login,
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