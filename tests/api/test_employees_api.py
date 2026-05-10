"""
API tests — direct backend validation.

These run faster than UI tests, so they go in the smoke pack.
Catch contract changes before any UI test even gets to render.
"""
from __future__ import annotations

import allure
import pytest

from src.api.clients.employee_client import EmployeeClient


@allure.epic("API")
@allure.feature("Employees")
class TestEmployeeApi:

    @allure.story("List endpoint returns 200 + list shape")
    @pytest.mark.smoke
    @pytest.mark.api
    def test_list_employees_returns_200(self, employee_client: EmployeeClient):
        response = employee_client.get(employee_client.RESOURCE, params={"limit": 5})
        employee_client.expect_status(response, 200)
        body = response.json()
        assert "data" in body, "Response missing 'data' envelope"
        assert isinstance(body["data"], list)

    @allure.story("Search by name endpoint")
    @pytest.mark.regression
    @pytest.mark.api
    def test_search_by_name(self, employee_client: EmployeeClient):
        results = employee_client.search_by_name("Admin")
        assert isinstance(results, list)

    @allure.story("Pagination respects limit param")
    @pytest.mark.regression
    @pytest.mark.api
    @pytest.mark.parametrize("limit", [1, 5, 10])
    def test_pagination_limit_is_respected(self, employee_client: EmployeeClient, limit: int):
        results = employee_client.list_employees(limit=limit)
        assert len(results) <= limit
