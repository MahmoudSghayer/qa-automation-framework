"""
Integration test — the *kind* of test that catches real bugs in production.

Flow:
    1. Create an employee via UI
    2. Verify the employee exists via API
    3. Verify the employee row exists in the database
    4. Clean up via API

This proves the three layers (presentation, service, persistence) agree.
"""
from __future__ import annotations

import allure
import pytest

from src.api.clients.employee_client import EmployeeClient
from src.db.queries import EmployeeQueries
from src.pages.pim_page import PimPage
from src.utils.data_factory import EmployeeData


@allure.epic("Integration")
@allure.feature("UI ⇄ API ⇄ DB consistency")
@pytest.mark.integration
class TestEmployeeEndToEnd:

    @allure.story("Create via UI → visible via API → row exists in DB")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    def test_employee_created_via_ui_visible_via_api_and_db(
        self,
        authenticated_page,
        pim_page: PimPage,
        employee_client: EmployeeClient,
        employee_queries: EmployeeQueries,    # auto-skips if DB disabled
    ):
        emp = EmployeeData.random()

        with allure.step("UI → create employee"):
            pim_page.navigate()
            pim_page.add_employee(emp.first_name, emp.middle_name, emp.last_name, emp.employee_id)

        with allure.step("API → confirm employee returned by search"):
            api_results = employee_client.search_by_name(emp.first_name)
            matches = [e for e in api_results if e.get("firstName") == emp.first_name]
            assert matches, f"API did not return employee {emp.first_name}"
            emp_number = matches[0]["empNumber"]

        with allure.step("DB → row exists with expected employee_id"):
            row = employee_queries.find_by_id(emp.employee_id)
            assert row is not None, "Employee row missing from DB"
            assert row["emp_firstname"] == emp.first_name
            assert row["emp_lastname"] == emp.last_name

        with allure.step("Cleanup → delete via API"):
            employee_client.delete_employees([emp_number])
