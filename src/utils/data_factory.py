"""
Test data factories.

Why Faker over hard-coded data:
    - Each run gets unique data → no state collisions in shared envs
    - Realistic shapes catch real validation bugs
    - One place to make data deterministic for debugging (seed)
"""
from __future__ import annotations

from dataclasses import dataclass
from faker import Faker

fake = Faker()


@dataclass(frozen=True)
class EmployeeData:
    first_name: str
    middle_name: str
    last_name: str
    employee_id: str
    full_name: str

    @classmethod
    def random(cls) -> "EmployeeData":
        first = fake.first_name()
        middle = fake.first_name()
        last = fake.last_name()
        emp_id = f"AUTO-{fake.unique.random_number(digits=6)}"
        return cls(
            first_name=first,
            middle_name=middle,
            last_name=last,
            employee_id=emp_id,
            full_name=f"{first} {middle} {last}",
        )


def random_email() -> str:
    return fake.unique.email()


def seed(value: int = 1234) -> None:
    """Make a run reproducible."""
    Faker.seed(value)
