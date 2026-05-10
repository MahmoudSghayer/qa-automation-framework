"""
AuthClient — performs a real form-post login against the demo and
holds the resulting session cookie. Every other API client receives
this client's `session` so they're authenticated.

This mirrors how real apps with mixed UI/API auth work.
"""
from __future__ import annotations

import re

from src.api.clients.base_client import BaseApiClient
from src.core.exceptions import ApiResponseError
from src.utils.logger import logger


class AuthClient(BaseApiClient):
    LOGIN_PATH = "/web/index.php/auth/validate"
    LOGIN_PAGE = "/web/index.php/auth/login"

    def login(self, username: str, password: str) -> None:
        # 1. GET login page → grab CSRF token
        page = self.get(self.LOGIN_PAGE)
        self.expect_status(page, 200)
        match = re.search(r'name="_token"\s+value="([^"]+)"', page.text)
        token = match.group(1) if match else ""

        # 2. POST credentials
        payload = {"_token": token, "username": username, "password": password}
        resp = self.post(
            self.LOGIN_PATH,
            data=payload,
            allow_redirects=True,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # 3. Validate — successful login redirects to /dashboard
        if "dashboard" not in resp.url.lower():
            raise ApiResponseError(
                f"Login failed for user={username}; landed on {resp.url}",
                status_code=resp.status_code,
            )
        logger.info(f"✅ API login OK as {username}")

    def is_authenticated(self) -> bool:
        return any(c.name in {"orangehrm", "_orangehrm"} for c in self.session.cookies)
