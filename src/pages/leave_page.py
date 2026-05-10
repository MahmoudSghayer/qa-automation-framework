"""
Leave module page object.

Why this matters in the portfolio:
    Leave flows exercise form interactions that are common in real HR/ERP
    products: dropdowns, date pickers, conditional fields, multi-step
    submissions. Recruiters look for tests that prove you can handle these,
    not just text inputs.
"""
from __future__ import annotations

from playwright.sync_api import Page

from src.core.base_page import BasePage


class ApplyLeavePage(BasePage):
    URL_PATH = "/web/index.php/leave/applyLeave"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

        # Form fields — OrangeHRM uses custom dropdowns, not native <select>
        self.leave_type_dropdown = page.locator("//label[text()='Leave Type']/../..//div[contains(@class,'oxd-select-text')]")
        self.from_date_input     = page.locator("//label[text()='From Date']/../..//input")
        self.to_date_input       = page.locator("//label[text()='To Date']/../..//input")
        self.comment_textarea    = page.locator("//label[text()='Comment']/../..//textarea")
        self.apply_button        = page.get_by_role("button", name="Apply")
        self.toast_success       = page.locator(".oxd-toast--success")
        self.required_errors     = page.locator("span.oxd-input-field-error-message")

    # ---------------------------------------------------------- actions --
    def select_leave_type(self, leave_type: str) -> None:
        """Custom dropdown — must click then choose the option from the popup."""
        self.click(self.leave_type_dropdown, description="Leave type dropdown")
        option = self._page.get_by_role("option", name=leave_type)
        self.click(option, description=f"Leave type option: {leave_type}")

    def set_date_range(self, from_date: str, to_date: str) -> None:
        # OrangeHRM date format: YYYY-MM-DD
        self.fill(self.from_date_input, from_date, description="From date")
        # Click outside to close any open date picker
        self._page.keyboard.press("Escape")
        self.fill(self.to_date_input, to_date, description="To date")
        self._page.keyboard.press("Escape")

    def add_comment(self, text: str) -> None:
        self.fill(self.comment_textarea, text, description="Comment")

    def submit(self) -> None:
        self.click(self.apply_button, description="Apply button")

    def submit_empty(self) -> None:
        self.click(self.apply_button, description="Apply (empty form)")

    # ------------------------------------------------------------ reads --
    def was_submitted_successfully(self) -> bool:
        return self.is_visible(self.toast_success, timeout=8_000)

    def get_required_errors(self) -> list[str]:
        return [t.strip() for t in self.required_errors.all_text_contents() if t.strip()]


class LeaveListPage(BasePage):
    URL_PATH = "/web/index.php/leave/viewLeaveList"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.results_table = page.locator(".oxd-table")
        self.results_rows  = page.locator(".oxd-table-card")
        self.no_records    = page.get_by_text("No Records Found")
        self.search_button = page.get_by_role("button", name="Search")
        self.reset_button  = page.get_by_role("button", name="Reset")

    def get_results_count(self) -> int:
        return self.results_rows.count()

    def has_no_records(self) -> bool:
        return self.is_visible(self.no_records, timeout=3_000)
