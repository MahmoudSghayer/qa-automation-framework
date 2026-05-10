"""
Domain-specific exceptions.

Why not just raise AssertionError everywhere:
    Custom exceptions let CI dashboards group failures by category
    (env issue vs. real bug vs. test bug) which dramatically speeds
    up triage on a real team.
"""


class FrameworkError(Exception):
    """Base for every error raised by the framework itself."""


class ConfigurationError(FrameworkError):
    """Bad/missing config — almost always an environment problem, not a bug."""


class ElementNotFoundError(FrameworkError):
    """Locator did not resolve within timeout — UI bug or selector drift."""


class ApiResponseError(FrameworkError):
    """API returned unexpected status / shape."""

    def __init__(self, message: str, status_code: int | None = None, body: str | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class DatabaseError(FrameworkError):
    """DB connection or query failure."""


class TestDataError(FrameworkError):
    """Fixture or data file missing/invalid — test bug, not product bug."""
