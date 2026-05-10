"""
Pydantic models = free schema validation + IDE autocomplete.

If the API ever changes a field type, the test fails at parse time
with a clear message — not deep inside an assertion.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class EmployeeBase(BaseModel):
    firstName: str = Field(min_length=1, max_length=30)
    middleName: str = ""
    lastName: str = Field(min_length=1, max_length=30)
    employeeId: str | None = None


class EmployeeCreate(EmployeeBase):
    pass


class Employee(EmployeeBase):
    empNumber: int
    fullName: str | None = None


class ApiEnvelope(BaseModel):
    """OrangeHRM wraps every response in {data: ..., meta: ...}."""

    data: dict | list
    meta: dict = {}
