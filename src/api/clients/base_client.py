"""
BaseApiClient — every resource client (employees, leave, …) extends this.

Why not just use requests directly in tests:
    - Centralized retry policy (tenacity)
    - Centralized timeout
    - Centralized auth (the session cookie plumbing)
    - Centralized logging of every request/response
    - Centralized error translation (raise ApiResponseError, not generic HTTPError)

This is exactly how a real microservices SDK is structured.
"""
from __future__ import annotations

from typing import Any

import requests
from requests import Response, Session
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.core.exceptions import ApiResponseError
from src.utils.logger import logger


class BaseApiClient:
    def __init__(self, base_url: str, *, timeout: int = 15, retries: int = 2):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.session: Session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "qa-framework/1.0",
        })

    # ----------------------------------------------------------- internals --
    def _url(self, path: str) -> str:
        return f"{self.base_url}{path if path.startswith('/') else '/' + path}"

    def _log_request(self, method: str, url: str, **kw: Any) -> None:
        params = kw.get("params") or {}
        body = kw.get("json")
        logger.debug(f"→ {method} {url} params={params} body={body}")

    def _log_response(self, r: Response) -> None:
        logger.debug(f"← {r.status_code} {r.request.method} {r.url} ({len(r.content)}B)")

    @retry(
        retry=retry_if_exception_type((requests.ConnectionError, requests.Timeout)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        reraise=True,
    )
    def _request(self, method: str, path: str, **kwargs: Any) -> Response:
        url = self._url(path)
        kwargs.setdefault("timeout", self.timeout)
        self._log_request(method, url, **kwargs)
        response = self.session.request(method, url, **kwargs)
        self._log_response(response)
        return response

    # -------------------------------------------------------------- verbs --
    def get(self, path: str, **kw: Any) -> Response:
        return self._request("GET", path, **kw)

    def post(self, path: str, **kw: Any) -> Response:
        return self._request("POST", path, **kw)

    def put(self, path: str, **kw: Any) -> Response:
        return self._request("PUT", path, **kw)

    def delete(self, path: str, **kw: Any) -> Response:
        return self._request("DELETE", path, **kw)

    # -------------------------------------------------------- helpers ----
    @staticmethod
    def expect_status(response: Response, expected: int | tuple[int, ...]) -> None:
        codes = expected if isinstance(expected, tuple) else (expected,)
        if response.status_code not in codes:
            raise ApiResponseError(
                f"Expected status {codes}, got {response.status_code}",
                status_code=response.status_code,
                body=response.text[:500],
            )
