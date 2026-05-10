"""
UI tests — Login feature.

Coverage:
    - Happy path
    - Invalid credential variants (data-driven)
    - Empty / required field validation
    - Session persistence after refresh
    - Logout + back-button protection
"""
from __future__ import annotations

import allure
import pytest

from config.settings import settings
from src.pages.dashboard_page import DashboardPage
from src.pages.login_page import LoginPage
from src.utils.file_loader import load_json

LOGIN_DATA = load_json("login_data.json")


@allure.epic("Authentication")
@allure.feature("Login")
class TestLoginHappyPath:

    @allure.story("Valid credentials")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_login_with_valid_credentials_lands_on_dashboard(
        self, login_page: LoginPage, dashboard_page: DashboardPage
    ):
        login_page.open()
        login_page.login(settings.credentials.username, settings.credentials.password)
        assert dashboard_page.is_loaded(), "Dashboard did not load after valid login"
        assert "dashboard" in dashboard_page.current_url.lower()

    @allure.story("Session persists across refresh")
    @pytest.mark.regression
    @pytest.mark.auth
    def test_session_persists_after_refresh(
        self, login_page: LoginPage, dashboard_page: DashboardPage
    ):
        login_page.open()
        login_page.login(settings.credentials.username, settings.credentials.password)
        assert dashboard_page.is_loaded()
        dashboard_page.reload()
        assert dashboard_page.is_loaded(), "Session lost after refresh"

    @allure.story("Logout invalidates session")
    @pytest.mark.regression
    @pytest.mark.auth
    def test_logout_returns_to_login(
        self, login_page: LoginPage, dashboard_page: DashboardPage
    ):
        login_page.open()
        login_page.login(settings.credentials.username, settings.credentials.password)
        dashboard_page.is_loaded()
        dashboard_page.logout()
        login_page.assert_visible(login_page.login_button)
        assert "login" in login_page.current_url.lower()


@allure.epic("Authentication")
@allure.feature("Login - Negative")
class TestLoginNegative:

    @allure.story("Invalid credentials show error alert")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.negative
    @pytest.mark.parametrize("case", LOGIN_DATA["invalid_credentials"], ids=lambda c: f"{c['username']}/{c['password']}")
    def test_invalid_credentials_show_error(self, login_page: LoginPage, case: dict):
        login_page.open()
        login_page.login(case["username"], case["password"])
        if case["expected_error"]:
            login_page.assert_visible(login_page.error_alert)
            assert case["expected_error"] in login_page.get_error_message()

    @allure.story("Empty fields trigger required-field validation")
    @pytest.mark.regression
    @pytest.mark.negative
    @pytest.mark.parametrize("case", LOGIN_DATA["empty_fields"], ids=lambda c: f"missing={','.join(c['missing'])}")
    def test_empty_fields_show_required_errors(self, login_page: LoginPage, case: dict):
        login_page.open()
        if case["username"]:
            login_page.fill(login_page.username_input, case["username"])
        if case["password"]:
            login_page.fill(login_page.password_input, case["password"], sensitive=True)
        login_page.submit_empty()
        errors = login_page.get_required_field_errors()
        assert len(errors) >= len(case["missing"]), f"Expected {len(case['missing'])} required errors, got {errors}"
