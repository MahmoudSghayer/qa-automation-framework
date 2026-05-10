"""
Login page for OrangeHRM demo.

Locator strategy:
    - Prefer get_by_role / get_by_placeholder / get_by_text.
      They survive minor DOM refactors; CSS classes don't.
    - Reserved CSS for cases where there is no semantic anchor.
"""
from __future__ import annotations

from playwright.sync_api import Page

from src.core.base_page import BasePage


class LoginPage(BasePage):
    URL_PATH = "/web/index.php/auth/login"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

        # --- Locators (defined once, reused everywhere) ---
        self.username_input  = page.get_by_placeholder("Username")
        self.password_input  = page.get_by_placeholder("Password")
        self.login_button    = page.get_by_role("button", name="Login")
        self.error_alert     = page.locator(".oxd-alert-content-text")
        self.required_errors = page.locator("span.oxd-input-field-error-message")
        self.forgot_link     = page.get_by_text("Forgot your password?")

    # ----------------------------------------------------- public actions --
    def open(self) -> "LoginPage":
        self.navigate()
        self.assert_visible(self.username_input)
        return self

    def login(self, username: str, password: str) -> None:
        self.fill(self.username_input, username, description="Username field")
        self.fill(self.password_input, password, description="Password field", sensitive=True)
        self.click(self.login_button, description="Login button")

    def submit_empty(self) -> None:
        self.click(self.login_button, description="Login button (empty form)")

    # ------------------------------------------------------- read helpers --
    def get_error_message(self) -> str:
        return self.get_text(self.error_alert)

    def get_required_field_errors(self) -> list[str]:
        return [t.strip() for t in self.required_errors.all_text_contents() if t.strip()]
