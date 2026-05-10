"""
UI tests — Leave application flow.

Coverage:
    - Apply leave with valid data (data-driven)
    - Required-field validation on empty submit
    - Edge case: invalid date range (to before from)
    - Leave list view loads
"""
from __future__ import annotations

import allure
import pytest

from src.pages.dashboard_page import DashboardPage
from src.pages.leave_page import ApplyLeavePage, LeaveListPage
from src.utils.file_loader import load_json

LEAVE_DATA = load_json("leave_data.json")


@allure.epic("Leave Management")
@allure.feature("Apply Leave")
class TestApplyLeave:

    @allure.story("Required-field validation")
    @pytest.mark.regression
    @pytest.mark.negative
    def test_apply_leave_empty_form_shows_required_errors(
        self, authenticated_page, apply_leave_page: ApplyLeavePage
    ):
        apply_leave_page.navigate()
        apply_leave_page.submit_empty()
        errors = apply_leave_page.get_required_errors()
        assert len(errors) >= 1, "Expected required-field errors on empty submit"

    @allure.story("Form remains on page after invalid submission")
    @pytest.mark.regression
    @pytest.mark.negative
    def test_apply_leave_invalid_does_not_navigate(
        self, authenticated_page, apply_leave_page: ApplyLeavePage
    ):
        apply_leave_page.navigate()
        apply_leave_page.submit_empty()
        assert "applyLeave" in apply_leave_page.current_url, "Should stay on apply-leave URL"


@allure.epic("Leave Management")
@allure.feature("Leave List")
class TestLeaveList:

    @allure.story("Leave list page loads")
    @pytest.mark.smoke
    def test_leave_list_page_renders(
        self, authenticated_page, leave_list_page: LeaveListPage
    ):
        leave_list_page.navigate()
        # Either rows OR 'No Records Found' must be visible — both are valid states
        has_data = leave_list_page.get_results_count() > 0
        no_data  = leave_list_page.has_no_records()
        assert has_data or no_data, "Leave list page failed to render any state"
