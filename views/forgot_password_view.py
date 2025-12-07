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
    
    # Separate message text for each step
    step1_message = ft.Text(value="", size=14, text_align="center")
    step2_message = ft.Text(value="", size=14, text_align="center")
    step3_message = ft.Text(value="", size=14, text_align="center")

    # Header titles for each step
    step1_title = ft.Text("Reset Password", size=20, weight="bold", color="white")
    step2_title = ft.Text("Verify Code", size=20, weight="bold", color="white")
    step3_title = ft.Text("Set New Password", size=20, weight="bold", color="white")

    # Subtitles for each step
    step1_subtitle = ft.Text(
        "Enter your email to receive a reset code",
        size=14,
        color="#b3b3b3",
        text_align="center"
    )
    step2_subtitle = ft.Text(
        "",
        size=14,
        color="#b3b3b3",
        text_align="center"
    )
    step3_subtitle = ft.Text(
        "Enter your new password",
        size=14,
        color="#b3b3b3",
        text_align="center"
    )

    # Containers for different steps
    step1_container = ft.Column(visible=True, spacing=10, horizontal_alignment="center")
    step2_container = ft.Column(visible=False, spacing=10, horizontal_alignment="center")
    step3_container = ft.Column(visible=False, spacing=10, horizontal_alignment="center")

    # Back to login
    def go_to_login(e):
        page.go("/login")

    # Header with back button and title
    header = ft.Container(
        content=ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=go_to_login,
                    icon_color="white",
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            step1_title,
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

    # Step 1: Request Reset Code
    def handle_send_code(e):
        email = email_input.value.strip()

        # Validation
        if not email:
            step1_message.value = "Please enter your email"
            step1_message.color = "red"
            page.update()
            return

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            step1_message.value = "Invalid email format"
            step1_message.color = "red"
            page.update()
            return

        # Show loading
        step1_message.value = "Sending reset code..."
        step1_message.color = "blue"
        page.update()

        # Send code
        success, msg = send_reset_code(email)

        if success:
            user_email["value"] = email
            step1_message.value = f"{msg}"
            step1_message.color = "green"
            page.update()
            
            # Wait a bit to show success message
            import time
            time.sleep(1)
            
            # Move to step 2
            current_step["value"] = 2
            step1_container.visible = False
            step2_container.visible = True
            
            # Clear step1 message
            step1_message.value = ""
            
            # Update header title and subtitle
            header.content.controls[1].content.controls[0] = step2_title
            step2_subtitle.value = f"Code sent to: {email}"
            
            page.update()
        else:
            step1_message.value = f"{msg}"
            step1_message.color = "red"
            page.update()

    # Step 2: Verify Code
    def handle_verify_code(e):
        code = code_input.value.strip()

        if not code:
            step2_message.value = "Please enter the code"
            step2_message.color = "red"
            page.update()
            return

        if len(code) != 6 or not code.isdigit():
            step2_message.value = "Code must be 6 digits"
            step2_message.color = "red"
            page.update()
            return

        # Show verifying message
        step2_message.value = "Verifying code..."
        step2_message.color = "blue"
        page.update()

        # Verify code
        valid, msg = verify_reset_code(user_email["value"], code)

        if valid:
            step2_message.value = f"{msg}"
            step2_message.color = "green"
            page.update()
            
            # Wait a bit to show success message
            import time
            time.sleep(1)
            
            # Move to step 3
            current_step["value"] = 3
            step2_container.visible = False
            step3_container.visible = True
            
            # Clear step2 message
            step2_message.value = ""
            
            # Update header title
            header.content.controls[1].content.controls[0] = step3_title
            
            page.update()
        else:
            step2_message.value = f"{msg}"
            step2_message.color = "red"
            page.update()

    # Step 3: Reset Password
    def handle_reset_password(e):
        new_pw = new_password_input.value.strip()
        confirm_pw = confirm_password_input.value.strip()
        code = code_input.value.strip()

        # Validation
        if not new_pw or not confirm_pw:
            step3_message.value = "Please fill in all fields"
            step3_message.color = "red"
            page.update()
            return

        if new_pw != confirm_pw:
            step3_message.value = "Passwords do not match"
            step3_message.color = "red"
            page.update()
            return

        if len(new_pw) < 6:
            step3_message.value = "Password must be at least 6 characters"
            step3_message.color = "red"
            page.update()
            return

        # Show resetting message
        step3_message.value = "Resetting password..."
        step3_message.color = "blue"
        page.update()

        # Reset password
        success, msg = reset_password(user_email["value"], code, new_pw)

        if success:
            step3_message.value = f"{msg} Redirecting to login..."
            step3_message.color = "green"
            page.update()
            
            import time
            time.sleep(2)
            page.go("/login")
        else:
            step3_message.value = f"{msg}"
            step3_message.color = "red"
            page.update()

    # Resend Code
    def handle_resend_code(e):
        step2_message.value = "Resending code..."
        step2_message.color = "blue"
        page.update()

        success, msg = send_reset_code(user_email["value"])
        
        if success:
            step2_message.value = f"{msg}"
            step2_message.color = "green"
        else:
            step2_message.value = f"{msg}"
            step2_message.color = "red"

        page.update()

    # Build Step 1 Container
    step1_container.controls = [
        step1_subtitle,
        ft.Container(height=10),
        email_input,
        primary_button("Send Reset Code", on_click=handle_send_code),
        ft.Container(height=5),
        step1_message,  # Use step1_message
    ]

    # Build Step 2 Container
    step2_container.controls = [
        step2_subtitle,
        ft.Container(height=10),
        code_input,
        primary_button("Verify Code", on_click=handle_verify_code),
        ft.TextButton(
            "Resend Code",
            on_click=handle_resend_code,
            style=ft.ButtonStyle(color="#E50914"),
        ),
        ft.Container(height=5),
        step2_message,  # Use step2_message
    ]

    # Build Step 3 Container
    step3_container.controls = [
        step3_subtitle,
        ft.Container(height=10),
        new_password_input,
        confirm_password_input,
        primary_button("Reset Password", on_click=handle_reset_password),
        ft.Container(height=5),
        step3_message,  #Use step3_message
    ]

    # Main layout
    layout = ft.Column(
        [
            header,
            ft.Container(height=20),
            step1_container,
            step2_container,
            step3_container,
        ],
        alignment="start",
        horizontal_alignment="center",
        spacing=0,
    )

    page.add(layout)


if __name__ == "__main__":
    ft.app(target=main)