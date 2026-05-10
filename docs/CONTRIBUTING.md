# Contributing

This file is also useful as a **"how the team would extend this framework"** reference for anyone reviewing the repo.

## Branch strategy

- `main` — protected, deployable, CI must be green
- `develop` — integration branch
- `feat/<short-name>` — new tests / features
- `fix/<short-name>` — flake fixes / bug fixes
- `chore/<short-name>` — deps, CI tweaks, docs

## Commit messages — Conventional Commits

```
<type>(<scope>): <subject>

<body>
```

| Type | When |
|---|---|
| `feat` | new test / new page object / new feature |
| `fix` | bugfix in framework code or selector |
| `test` | adding or improving tests only |
| `refactor` | code change with no behavior change |
| `docs` | README / docs only |
| `ci` | GitHub Actions, Docker |
| `chore` | deps, version bumps, config |

Examples:

```
feat(pim): add employee search with autocomplete handling
fix(login): wait for spinner before asserting dashboard
ci(allure): publish history to gh-pages on main
test(api): cover 404 response on unknown employee id
refactor(base-page): extract retry logic into decorator
```

## Adding a new feature area

1. **Page object** in `src/pages/<feature>_page.py` extending `BasePage`.
2. **API client** (if needed) in `src/api/clients/<feature>_client.py` extending `BaseApiClient`.
3. **Pydantic models** in `src/api/models/<feature>.py` for request/response shapes.
4. **DB queries** (if needed) in `src/db/queries.py` (or a new module).
5. **Fixtures** wired in `conftest.py` — one line per object.
6. **Test data** in `tests/data/<feature>_data.json`.
7. **Tests** in `tests/ui/<feature>/` and/or `tests/api/`.

Then run:

```bash
pytest tests/ui/<feature> -v --headed
```

## Locator conventions

Follow this priority order when adding selectors:

1. `page.get_by_role("button", name="Save")`
2. `page.get_by_label("Username")`
3. `page.get_by_placeholder("Search")`
4. `page.get_by_text("Welcome", exact=True)`
5. `page.get_by_test_id("submit")` *(if app exposes them)*
6. `page.locator(".some-class")` — only if nothing above works
7. **XPath — last resort.** Use only for `//label[text()='X']/../..//input` patterns where there's no semantic anchor.

Locators always live in `__init__` of the page object — never inline inside a method. Defining once allows IDE refactor-by-rename.

## Test design rules

- A test does **one thing** and asserts it.
- Setup goes in fixtures, never in the test body.
- Cleanup uses fixture teardown (`yield`), never `try/finally` in the test.
- Tests are independent — any test must pass in isolation (`pytest -k <test_name>`).
- No `time.sleep(...)`. Use `wait_for_url`, `expect(...).to_be_visible(timeout=...)`, or `wait_for_load_state`.
- No bare `assert ...` — always pass a message: `assert x, "what was expected vs. seen"`.
- Mark the test: `@pytest.mark.smoke`, `@pytest.mark.regression`, `@pytest.mark.negative`, etc.
- Add Allure decorators: `@allure.epic`, `@allure.feature`, `@allure.story`, `@allure.severity`.

## Pre-commit checklist

```bash
ruff check src tests config        # lint
black src tests config             # format
mypy src                           # types
pytest -m smoke -n auto            # smoke green
```

CI gates on all four. Run locally — saves a round trip.

## Code review checklist

- [ ] One concern per PR (a feature, or a fix, or a refactor — not all three).
- [ ] All new tests have markers and Allure decorators.
- [ ] No `time.sleep` introduced.
- [ ] No locator duplication — defined once in the page object `__init__`.
- [ ] Test names are full sentences: `test_login_with_invalid_password_shows_error`, not `test_login_2`.
- [ ] If a test was changed to be skipped/xfail, there's a linked issue explaining why.
- [ ] If a flake retry was added, there's a comment explaining the root cause and follow-up work.

## Definition of Done

A test/feature is "done" when:

- ✅ It passes 5 consecutive runs in CI (no flake).
- ✅ It's covered by a marker so it's findable.
- ✅ Allure shows the right epic/feature/story tree.
- ✅ Failure artifacts (screenshot/video/trace) are visible and useful.
- ✅ Documentation updated if a new pattern was introduced.
