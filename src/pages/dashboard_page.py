"""Dashboard — the post-login landing page."""
from __future__ import annotations

from playwright.sync_api import Page

from src.core.base_page import BasePage


class DashboardPage(BasePage):
    URL_PATH = "/web/index.php/dashboard/index"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.header             = page.locator("h6.oxd-topbar-header-breadcrumb-module")
        self.user_dropdown      = page.locator(".oxd-userdropdown-tab")
        self.logout_link        = page.get_by_role("menuitem", name="Logout")
        self.side_menu_search   = page.get_by_placeholder("Search")
        self.quick_launch_cards = page.locator(".orangehrm-quick-launch-card")

    def is_loaded(self) -> bool:
        return self.is_visible(self.header, timeout=10_000) and "Dashboard" in self.get_text(self.header)

    def logout(self) -> None:
        self.click(self.user_dropdown, description="User dropdown")
        self.click(self.logout_link, description="Logout link")

    def navigate_to(self, menu_item: str) -> None:
        """Click any side-nav item by visible name (PIM, Leave, Admin, …)."""
        self.click(
            self._page.get_by_role("link", name=menu_item),
            description=f"Side nav → {menu_item}",
        )
