"""EmployeeClient — CRUD against /api/v2/pim/employees."""
from __future__ import annotations

from src.api.clients.base_client import BaseApiClient
from src.api.models.employee import Employee, EmployeeCreate


class EmployeeClient(BaseApiClient):
    RESOURCE = "/pim/employees"

    def __init__(self, base_url: str, session, **kw):
        super().__init__(base_url, **kw)
        # Re-use the authenticated session from AuthClient
        self.session = session

    def list_employees(self, *, limit: int = 50, offset: int = 0) -> list[dict]:
        r = self.get(self.RESOURCE, params={"limit": limit, "offset": offset})
        self.expect_status(r, 200)
        return r.json().get("data", [])

    def get_employee(self, emp_number: int) -> dict:
        r = self.get(f"{self.RESOURCE}/{emp_number}")
        self.expect_status(r, 200)
        return r.json().get("data", {})

    def create_employee(self, payload: EmployeeCreate) -> Employee:
        r = self.post(self.RESOURCE, json=payload.model_dump(exclude_none=True))
        self.expect_status(r, (200, 201))
        return Employee.model_validate(r.json()["data"])

    def delete_employees(self, emp_numbers: list[int]) -> None:
        r = self.delete(self.RESOURCE, json={"ids": emp_numbers})
        self.expect_status(r, (200, 204))

    def search_by_name(self, name: str) -> list[dict]:
        r = self.get(self.RESOURCE, params={"nameOrId": name})
        self.expect_status(r, 200)
        return r.json().get("data", [])
