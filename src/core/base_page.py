"""
BasePage — the single integration point with Playwright.

Design rules enforced by this class:
    1. Tests NEVER call page.click / page.fill directly. They call
       page-object methods, which call BasePage methods.
    2. Every interaction is logged at DEBUG with the locator description.
    3. Every interaction has an explicit, configurable timeout.
    4. Auto-screenshot on assertion failure is handled in conftest.py;
       this class only exposes the helper.
    5. No XPath unless absolutely necessary. Prefer role/text/test-id locators.

Why this matters for scaling:
    A 500-test suite with raw page.click calls becomes unmaintainable the
    moment Playwright deprecates an option or your app adds a global
    loading spinner. Funneling every interaction through here means
    framework-wide changes are one-file diffs.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from playwright.sync_api import Locator, Page, TimeoutError as PWTimeoutError, expect

from src.core.exceptions import ElementNotFoundError
from src.utils.logger import logger


class BasePage:
    """Abstract base for all page objects."""

    # Subclasses set this; used by navigate()
    URL_PATH: str = ""

    def __init__(self, page: Page, base_url: str):
        self._page = page
        self._base_url = base_url.rstrip("/")

    # ---------------------------------------------------------------- nav --
    def navigate(self, path: str | None = None) -> None:
        url = f"{self._base_url}{path or self.URL_PATH}"
        logger.info(f"Navigating → {url}")
        self._page.goto(url, wait_until="domcontentloaded")

    def reload(self) -> None:
        logger.debug("Reloading page")
        self._page.reload(wait_until="domcontentloaded")

    @property
    def current_url(self) -> str:
        return self._page.url

    @property
    def title(self) -> str:
        return self._page.title()

    # ---------------------------------------------------------- interaction --
    def click(self, locator: Locator, *, description: str = "", timeout: int | None = None) -> None:
        desc = description or self._describe(locator)
        logger.debug(f"Click → {desc}")
        try:
            locator.click(timeout=timeout)
        except PWTimeoutError as e:
            raise ElementNotFoundError(f"Click timed out on: {desc}") from e

    def fill(self, locator: Locator, value: str, *, description: str = "", sensitive: bool = False) -> None:
        desc = description or self._describe(locator)
        shown = "***" if sensitive else value
        logger.debug(f"Fill → {desc} = {shown!r}")
        try:
            locator.fill(value)
        except PWTimeoutError as e:
            raise ElementNotFoundError(f"Fill timed out on: {desc}") from e

    def type_slowly(self, locator: Locator, value: str, *, delay_ms: int = 50) -> None:
        """For inputs with debounced JS handlers (autocomplete dropdowns)."""
        locator.click()
        locator.type(value, delay=delay_ms)

    def select_option(self, locator: Locator, *, label: str | None = None, value: str | None = None) -> None:
        logger.debug(f"Select → {self._describe(locator)} (label={label}, value={value})")
        if label:
            locator.select_option(label=label)
        elif value:
            locator.select_option(value=value)
        else:
            raise ValueError("select_option requires label or value")

    def get_text(self, locator: Locator) -> str:
        return (locator.text_content() or "").strip()

    def is_visible(self, locator: Locator, *, timeout: int = 5_000) -> bool:
        try:
            locator.wait_for(state="visible", timeout=timeout)
            return True
        except PWTimeoutError:
            return False

    # ---------------------------------------------------------------- waits --
    def wait_for_url_contains(self, fragment: str, *, timeout: int = 15_000) -> None:
        logger.debug(f"Wait for URL contains: {fragment}")
        self._page.wait_for_url(f"**/*{fragment}*", timeout=timeout)

    def wait_for_load(self, state: str = "networkidle") -> None:
        self._page.wait_for_load_state(state)

    # ----------------------------------------------------------- assertions --
    def assert_visible(self, locator: Locator, *, timeout: int = 10_000) -> None:
        """Auto-retrying visibility assertion — the Playwright way."""
        expect(locator).to_be_visible(timeout=timeout)

    def assert_text(self, locator: Locator, expected: str, *, timeout: int = 10_000) -> None:
        expect(locator).to_have_text(expected, timeout=timeout)

    def assert_contains_text(self, locator: Locator, expected: str, *, timeout: int = 10_000) -> None:
        expect(locator).to_contain_text(expected, timeout=timeout)

    # --------------------------------------------------------- screenshots --
    def take_screenshot(self, name: str) -> Path:
        path = Path("reports/screenshots") / f"{name}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        self._page.screenshot(path=str(path), full_page=True)
        logger.info(f"📸 Screenshot saved → {path}")
        return path

    # ----------------------------------------------------------- internals --
    @staticmethod
    def _describe(locator: Locator) -> str:
        """Short string for logs — Playwright's repr is verbose."""
        try:
            return str(locator).replace("\n", " ")[:120]
        except Exception:
            return "<locator>"
