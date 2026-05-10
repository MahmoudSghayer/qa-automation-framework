"""
Query objects — every query the framework issues lives here.

Why centralize:
    - DBAs review one file, not 50 test files
    - SQL refactors (table renames, schema versioning) touch one file
    - Tests stay readable (employee.find_by_name(...) vs raw SQL)
"""
from __future__ import annotations

from src.db.db_client import DatabaseClient


class EmployeeQueries:
    def __init__(self, db: DatabaseClient):
        self._db = db

    def find_by_full_name(self, first: str, last: str) -> dict | None:
        return self._db.fetch_one(
            "SELECT emp_number, emp_firstname, emp_lastname, employee_id "
            "FROM hs_hr_employee "
            "WHERE emp_firstname = :first AND emp_lastname = :last "
            "LIMIT 1",
            first=first,
            last=last,
        )

    def count_active_employees(self) -> int:
        row = self._db.fetch_one(
            "SELECT COUNT(*) AS total FROM hs_hr_employee "
            "WHERE termination_id IS NULL"
        )
        return int(row["total"]) if row else 0

    def find_by_id(self, employee_id: str) -> dict | None:
        return self._db.fetch_one(
            "SELECT * FROM hs_hr_employee WHERE employee_id = :eid LIMIT 1",
            eid=employee_id,
        )
