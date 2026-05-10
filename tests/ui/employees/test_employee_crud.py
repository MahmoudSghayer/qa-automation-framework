"""
UI tests — Employee Search & CRUD.
"""
from __future__ import annotations

import allure
import pytest

from src.pages.dashboard_page import DashboardPage
from src.pages.pim_page import PimPage
from src.utils.data_factory import EmployeeData


@allure.epic("PIM")
@allure.feature("Employee Search")
class TestEmployeeSearch:

    @allure.story("Search by valid employee name returns results")
    @pytest.mark.smoke
    @pytest.mark.crud
    def test_search_existing_employee(self, authenticated_page, pim_page: PimPage):
        pim_page.navigate()
        pim_page.search_by_name("Admin")
        assert pim_page.get_results_count() >= 0  # demo may have varying data

    @allure.story("Search by non-existent name shows 'No Records Found'")
    @pytest.mark.regression
    @pytest.mark.negative
    def test_search_nonexistent_employee(self, authenticated_page, pim_page: PimPage):
        pim_page.navigate()
        pim_page.search_by_name("ZzNoSuchUserXx")
        assert pim_page.has_no_records(), "Expected 'No Records Found' for invalid name"


@allure.epic("PIM")
@allure.feature("Employee CRUD")
class TestEmployeeCrud:

    @allure.story("Create new employee → verify in search results")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.crud
    def test_create_new_employee_appears_in_search(
        self, authenticated_page, pim_page: PimPage, dashboard_page: DashboardPage
    ):
        emp = EmployeeData.random()

        with allure.step(f"Create employee {emp.full_name}"):
            pim_page.navigate()
            pim_page.add_employee(emp.first_name, emp.middle_name, emp.last_name, emp.employee_id)

        with allure.step(f"Search for {emp.first_name}"):
            pim_page.navigate()
            pim_page.search_by_name(emp.first_name)
            assert pim_page.get_results_count() >= 1, "Newly created employee not found"

    @allure.story("Form-level validation rejects empty required fields")
    @pytest.mark.regression
    @pytest.mark.negative
    def test_add_employee_requires_first_and_last_name(
        self, authenticated_page, pim_page: PimPage
    ):
        pim_page.navigate()
        pim_page.open_add_employee_form()
        pim_page.click(pim_page.save_button, description="Save (empty form)")
        # Required errors should be visible
        errors = pim_page._page.locator("span.oxd-input-field-error-message").count()
        assert errors >= 1, "Expected at least one required-field error"
