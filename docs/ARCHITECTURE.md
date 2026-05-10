# Architecture Deep Dive

This document is the "why" behind the framework. The README covers the "what" and "how".

## 1. Layered architecture

```
┌─────────────────────────────────────────────────────────┐
│  Test Layer        tests/ui/  tests/api/  tests/integration/
│                    – No framework logic
│                    – No locators
│                    – Reads as a spec
├─────────────────────────────────────────────────────────┤
│  Domain Layer      src/pages/   src/api/clients/   src/db/queries/
│                    – One module per domain concept
│                    – Encapsulates *how*; tests express *what*
├─────────────────────────────────────────────────────────┤
│  Core Layer        src/core/
│                    – BasePage, custom exceptions
│                    – The only place that imports Playwright
├─────────────────────────────────────────────────────────┤
│  Cross-cutting     config/   src/utils/
│                    – Settings, logger, factories, file IO
└─────────────────────────────────────────────────────────┘
```

**Rule:** dependencies flow downward only. A page object never imports a test, core never imports pages, config never imports anything domain-specific.

## 2. Key design decisions

### Why Playwright over Selenium

- Auto-waiting reduces flakiness more than any retry strategy can.
- Single API across Chromium, Firefox, WebKit.
- Built-in tracing tool that's better than any third-party debug tool I've used in Selenium-land.
- Native test isolation via browser contexts (no cookie bleed between tests).

### Why `BasePage`

A 500-test suite where each test calls `page.click(...)` directly is a tax on every framework upgrade. Centralizing means:

- One place to add custom waits (e.g. wait for app-specific spinner).
- One place to wire logging.
- One place to handle Playwright API breaking changes.
- Tests become pure intent: `login_page.login(user, pwd)`.

### Why a separate API client layer

Three reasons:

1. **Speed**: API smoke runs in seconds, UI smoke in minutes. Catch regressions earlier.
2. **Test data setup**: Creating 50 employees via UI for a search test is wasteful. The API does it instantly.
3. **Real bugs**: Inconsistencies between layers (UI says "saved", API returns 500, DB has no row) are common and only catchable with a multi-layer test.

### Why Pydantic models for API

Free schema validation. If the backend renames `firstName` to `first_name`, every API test fails at *parse time* with a precise message — not 50 lines deep into an assertion.

### Why YAML + env vars (not just one or the other)

- YAML for shape (what config exists, what defaults are sane).
- Env vars for values (what changes per environment).
- This is the 12-Factor split, used by every cloud-native app.

### Why Loguru, not stdlib logging

Multi-process safety with `pytest-xdist` is non-trivial in stdlib. Loguru's `enqueue=True` handles it transparently.

### Why centralized SQL in `queries.py`

DBAs and senior backend engineers can review every query the test suite issues by opening one file. Schema migrations break tests in a predictable, fixable place.

## 3. How the layers cooperate

A typical integration test:

```
tests/integration/test_employee_end_to_end.py
        │
        │ uses fixture
        ▼
   pim_page (PimPage)               ──▶ src/pages/pim_page.py
        │                                │ extends
        │                                ▼
        │                         src/core/base_page.py ──▶ Playwright
        │
        │ uses fixture
        ▼
   employee_client                  ──▶ src/api/clients/employee_client.py
        │                                │ extends
        │                                ▼
        │                         src/api/clients/base_client.py ──▶ requests
        │
        │ uses fixture
        ▼
   employee_queries                 ──▶ src/db/queries.py
                                         │ uses
                                         ▼
                                  src/db/db_client.py ──▶ SQLAlchemy
```

Every fixture is composed; nothing is constructed inside a test.

## 4. Failure handling philosophy

A failing test should produce, in this order:

1. A precise assertion message (Playwright's `expect` does this well).
2. A screenshot (full page, attached to Allure).
3. A video of the test (if enabled).
4. A Playwright trace (timeline, network, console, DOM snapshots).
5. A log file with DEBUG-level breadcrumbs.

All five are wired up in `conftest.py` automatically. No test author writes any of this.

## 5. Parallelism strategy

- **`pytest-xdist -n auto`**: spreads tests across CPU cores.
- **Fresh browser context per test**: zero shared state.
- **Session-scoped browser**: launching Chromium is the slow part; we share one launch.
- **Session-scoped API auth**: log in once, reuse the cookie.
- **Faker-driven unique data**: no naming collisions.

A 100-test suite that takes 12 minutes serial drops to ~2 minutes on an 8-core CI runner.

## 6. Extension points

Adding a new feature area is mechanical:

1. Add a page object in `src/pages/`.
2. (Optional) add an API client in `src/api/clients/`.
3. Add a fixture in `conftest.py` (one line).
4. Write tests in `tests/ui/<feature>/`.

Adding a new environment:

1. Drop a `config/<envname>.yaml`.
2. `TEST_ENV=<envname> pytest`.

That's it.
