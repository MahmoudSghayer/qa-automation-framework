"""
PIM page — Personal Information Management (employees CRUD).

This is where we exercise create / search / edit / delete flows.
"""
from __future__ import annotations

from playwright.sync_api import Page

from src.core.base_page import BasePage


class PimPage(BasePage):
    URL_PATH = "/web/index.php/pim/viewEmployeeList"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

        # --- List view ---
        self.add_button         = page.get_by_role("button", name="Add")
        self.search_first_name  = page.locator("//label[text()='Employee Name']/../..//input")
        self.search_button      = page.get_by_role("button", name="Search")
        self.reset_button       = page.get_by_role("button", name="Reset")
        self.results_table      = page.locator(".oxd-table")
        self.results_rows       = page.locator(".oxd-table-card")
        self.result_count       = page.locator(".orangehrm-horizontal-padding .oxd-text--span")
        self.no_records_text    = page.get_by_text("No Records Found")

        # --- Add Employee form ---
        self.first_name_input   = page.get_by_placeholder("First Name")
        self.middle_name_input  = page.get_by_placeholder("Middle Name")
        self.last_name_input    = page.get_by_placeholder("Last Name")
        self.employee_id_input  = page.locator(
            "//label[text()='Employee Id']/../..//input"
        )
        self.save_button        = page.get_by_role("button", name="Save")
        self.toast_success      = page.locator(".oxd-toast--success")

    # ------------------------------------------------------------- search --
    def search_by_name(self, name: str) -> None:
        # The Employee Name field has autocomplete — must type slowly
        self.type_slowly(self.search_first_name, name)
        # Wait for autocomplete dropdown then commit
        self._page.wait_for_timeout(800)
        self.click(self.search_button, description="Search button")
        self.wait_for_load("networkidle")

    def reset_filters(self) -> None:
        self.click(self.reset_button)

    def get_results_count(self) -> int:
        return self.results_rows.count()

    def has_no_records(self) -> bool:
        return self.is_visible(self.no_records_text, timeout=3_000)

    # --------------------------------------------------------------- crud --
    def open_add_employee_form(self) -> None:
        self.click(self.add_button, description="Add Employee button")
        self.assert_visible(self.first_name_input)

    def add_employee(self, first: str, middle: str, last: str, employee_id: str | None = None) -> None:
        self.open_add_employee_form()
        self.fill(self.first_name_input, first, description="First name")
        self.fill(self.middle_name_input, middle, description="Middle name")
        self.fill(self.last_name_input, last, description="Last name")
        if employee_id is not None:
            self.employee_id_input.fill("")
            self.fill(self.employee_id_input, employee_id, description="Employee ID")
        self.click(self.save_button, description="Save")
        self.assert_visible(self.toast_success, timeout=10_000)

    def delete_first_result(self) -> None:
        first_row_delete = self.results_rows.first.locator("button.oxd-icon-button").nth(0)
        self.click(first_row_delete, description="Delete (row 1)")
        self.click(self._page.get_by_role("button", name="Yes, Delete"))
        self.assert_visible(self.toast_success, timeout=10_000)
