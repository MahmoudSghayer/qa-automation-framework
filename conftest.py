"""
Root pytest configuration.

Lives at repo root so that:
    - `tests/` and `src/` both resolve as importable packages
    - Fixtures are visible to every test directory automatically
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Iterator

import allure
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

# Make src/ importable without installing as a package
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from config.settings import settings                           # noqa: E402
from src.api.clients.auth_client import AuthClient             # noqa: E402
from src.api.clients.employee_client import EmployeeClient     # noqa: E402
from src.db.db_client import DatabaseClient                    # noqa: E402
from src.db.queries import EmployeeQueries                     # noqa: E402
from src.pages.dashboard_page import DashboardPage             # noqa: E402
from src.pages.leave_page import ApplyLeavePage, LeaveListPage # noqa: E402
from src.pages.login_page import LoginPage                     # noqa: E402
from src.pages.pim_page import PimPage                         # noqa: E402
from src.utils.logger import logger                            # noqa: E402

# ============================================================ session ====


def pytest_configure(config: pytest.Config) -> None:
    """Print active environment once, at the top of the run."""
    logger.info("=" * 70)
    logger.info(f"  TEST_ENV     : {settings.environment}")
    logger.info(f"  BASE_URL     : {settings.app.base_url}")
    logger.info(f"  BROWSER      : {settings.browser.default} (headless={settings.browser.headless})")
    logger.info(f"  WORKERS      : {settings.workers}")
    logger.info(f"  DB enabled   : {settings.database.enabled}")
    logger.info("=" * 70)


# ============================================================ Playwright ====


@pytest.fixture(scope="session")
def playwright_instance() -> Iterator[Playwright]:
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright) -> Iterator[Browser]:
    name = settings.browser.default
    launcher = getattr(playwright_instance, name)
    b = launcher.launch(headless=settings.browser.headless, slow_mo=int(os.getenv("SLOW_MO", "0")))
    logger.info(f"Browser launched: {name}")
    yield b
    b.close()


@pytest.fixture()
def context(browser: Browser, request: pytest.FixtureRequest) -> Iterator[BrowserContext]:
    """
    Fresh context per test → isolated cookies, storage, permissions.
    Video recording follows config; trace can be turned on per-test
    via @pytest.mark.trace.
    """
    record_video_dir = "reports/videos" if settings.browser.video != "off" else None

    ctx = browser.new_context(
        viewport={"width": settings.browser.viewport_width, "height": settings.browser.viewport_height},
        record_video_dir=record_video_dir,
        record_video_size={"width": 1280, "height": 720} if record_video_dir else None,
        ignore_https_errors=True,
    )
    ctx.set_default_timeout(settings.browser.timeout_ms)
    ctx.set_default_navigation_timeout(settings.browser.navigation_timeout_ms)

    if settings.browser.trace != "off":
        ctx.tracing.start(screenshots=True, snapshots=True, sources=True)

    yield ctx

    # On failure, save trace and attach to allure
    failed = getattr(request.node, "rep_call", None) and request.node.rep_call.failed
    if settings.browser.trace != "off":
        trace_path = Path("reports") / f"trace-{request.node.name}.zip"
        ctx.tracing.stop(path=str(trace_path) if failed else None)
        if failed and trace_path.exists():
            allure.attach.file(str(trace_path), name="playwright-trace", extension="zip")

    ctx.close()


@pytest.fixture()
def page(context: BrowserContext, request: pytest.FixtureRequest) -> Iterator[Page]:
    pg = context.new_page()
    yield pg

    # On failure: screenshot + attach video
    rep = getattr(request.node, "rep_call", None)
    if rep and rep.failed:
        try:
            shot = Path("reports/screenshots") / f"FAIL-{request.node.name}.png"
            shot.parent.mkdir(parents=True, exist_ok=True)
            pg.screenshot(path=str(shot), full_page=True)
            allure.attach.file(str(shot), name="failure-screenshot", attachment_type=allure.attachment_type.PNG)
            logger.error(f"❌ Test failed — screenshot: {shot}")
        except Exception as e:                                        # noqa: BLE001
            logger.warning(f"Could not capture failure screenshot: {e}")

    pg.close()

    # Attach video to allure if recorded
    if rep and rep.failed and pg.video:
        try:
            video_path = pg.video.path()
            if video_path:
                allure.attach.file(video_path, name="failure-video", attachment_type=allure.attachment_type.WEBM)
        except Exception:                                             # noqa: BLE001
            pass


# ============================================================ Page Objects ====


@pytest.fixture()
def login_page(page: Page) -> LoginPage:
    return LoginPage(page, settings.app.base_url)


@pytest.fixture()
def dashboard_page(page: Page) -> DashboardPage:
    return DashboardPage(page, settings.app.base_url)


@pytest.fixture()
def pim_page(page: Page) -> PimPage:
    return PimPage(page, settings.app.base_url)


@pytest.fixture()
def apply_leave_page(page: Page) -> ApplyLeavePage:
    return ApplyLeavePage(page, settings.app.base_url)


@pytest.fixture()
def leave_list_page(page: Page) -> LeaveListPage:
    return LeaveListPage(page, settings.app.base_url)


@pytest.fixture()
def authenticated_page(login_page: LoginPage, dashboard_page: DashboardPage, page: Page) -> Page:
    """Reusable shortcut: returns a page already past the login gate."""
    login_page.open()
    login_page.login(settings.credentials.username, settings.credentials.password)
    dashboard_page.is_loaded()
    return page


# ============================================================ API ====


@pytest.fixture(scope="session")
def auth_client() -> AuthClient:
    client = AuthClient(
        base_url=settings.app.base_url,
        timeout=settings.api.timeout_seconds,
        retries=settings.api.retries,
    )
    client.login(settings.credentials.username, settings.credentials.password)
    return client


@pytest.fixture()
def employee_client(auth_client: AuthClient) -> EmployeeClient:
    return EmployeeClient(
        base_url=settings.app.api_base_url,
        session=auth_client.session,
        timeout=settings.api.timeout_seconds,
    )


# ============================================================ DB ====


@pytest.fixture(scope="session")
def db_client() -> Iterator[DatabaseClient | None]:
    if not settings.database.enabled:
        yield None
        return
    client = DatabaseClient(
        host=settings.database.host,
        port=settings.database.port,
        name=settings.database.name,
        user=settings.database.user,
        password=settings.database.password,
        pool_size=settings.database.pool_size,
        read_only=settings.database.read_only,
    )
    yield client
    client.close()


@pytest.fixture()
def employee_queries(db_client: DatabaseClient | None) -> EmployeeQueries:
    if db_client is None:
        pytest.skip("Database is disabled in this environment")
    return EmployeeQueries(db_client)


# ============================================================ hooks ====


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """Expose test outcome to fixtures (so we can screenshot on fail)."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Auto-tag tests by directory so `-m ui` and `-m api` work without manual marking."""
    for item in items:
        path = str(item.fspath)
        if "/tests/ui/" in path:
            item.add_marker(pytest.mark.ui)
        elif "/tests/api/" in path:
            item.add_marker(pytest.mark.api)
        elif "/tests/integration/" in path:
            item.add_marker(pytest.mark.integration)
