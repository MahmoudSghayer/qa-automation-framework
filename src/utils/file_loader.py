"""File loaders for parameterized test data."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from src.core.exceptions import TestDataError

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "tests" / "data"


def load_json(filename: str) -> Any:
    path = DATA_DIR / filename
    if not path.exists():
        raise TestDataError(f"Data file not found: {path}")
    with path.open() as f:
        return json.load(f)


def load_yaml(filename: str) -> Any:
    path = DATA_DIR / filename
    if not path.exists():
        raise TestDataError(f"Data file not found: {path}")
    with path.open() as f:
        return yaml.safe_load(f)
