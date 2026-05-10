# Execution Guide

Practical reference for running the suite in every supported way.

## Setup (once per machine)

```bash
# 1. Clone
git clone https://github.com/<your-username>/qa-automation-framework.git
cd qa-automation-framework

# 2. Virtualenv
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Python deps
pip install -r requirements.txt

# 4. Browsers
python -m playwright install --with-deps chromium firefox webkit

# 5. Local config
cp .env.example .env                # then edit credentials if not using demo defaults
```

Verify with:

```bash
pytest --collect-only -q
```

You should see ~15-20 collected tests with no errors.

---

## Common runs

| Goal | Command |
|---|---|
| Smoke, parallel, headless | `pytest -m smoke -n auto` |
| Single feature, debugging | `HEADLESS=false pytest tests/ui/login -v -s` |
| Full regression | `pytest -m regression --reruns 2` |
| API only (fast) | `pytest -m api` |
| Integration only | `pytest -m integration` |
| Single test | `pytest tests/ui/login/test_login.py::TestLoginHappyPath::test_login_with_valid_credentials_lands_on_dashboard` |
| By keyword | `pytest -k "invalid_credentials"` |
| Fail fast | `pytest -x` |
| Last-failed only | `pytest --lf` |
| With trace viewer auto-open | `pytest --tracing=on` then `playwright show-trace reports/trace-*.zip` |

---

## Environment switching

```bash
TEST_ENV=dev      pytest -m smoke      # config/dev.yaml
TEST_ENV=staging  pytest -m smoke      # default
TEST_ENV=prod     pytest -m smoke      # config/prod.yaml — DB is read-only
```

YAML defines shape, env vars override values. Precedence: env var > yaml > hardcoded default.

---

## Browser selection

```bash
BROWSER=firefox  pytest -m smoke
BROWSER=webkit   pytest -m smoke
HEADLESS=false   pytest -m smoke      # see what's happening
SLOW_MO=300      pytest -m smoke      # 300ms between actions for human pace
```

---

## Reporting

### Allure (rich, interactive)

```bash
pytest -m smoke                            # writes reports/allure-results/
./scripts/generate-report.sh               # builds HTML + opens browser
```

Requires the [Allure CLI](https://allurereport.org/docs/install/).

### Pytest-html (zero-dependency)

Open `reports/pytest-html/report.html` in any browser after a run. Self-contained, easy to email.

### Logs

```bash
tail -f reports/logs/framework_$(date +%F).log
```

DEBUG-level logs include every Playwright interaction with locator descriptions — invaluable when triaging flaky tests.

---

## Docker

```bash
# Build + run smoke in container
docker compose -f docker/docker-compose.yml up --build tests

# Different marker
MARKER=regression docker compose -f docker/docker-compose.yml up tests

# View report at http://localhost:5050
docker compose -f docker/docker-compose.yml up allure
```

The container uses the official Playwright base image, so browsers are pre-installed and dependency-pinned to match the Python `playwright` package version.

---

## CI/CD

| Trigger | Workflow | Pipeline |
|---|---|---|
| Push to `main`/`develop` | `ci.yml` | lint → smoke (Chromium + Firefox) → publish Allure |
| Pull request | `ci.yml` | lint → smoke |
| Nightly @ 02:00 UTC | `ci.yml` | + full regression |
| Manual | `ci.yml` (workflow_dispatch) | choose marker + env |
| Manual | `docker.yml` | run inside container (parity check) |

Failure artifacts (screenshots, videos, logs, Playwright traces) are retained for 14 days.

---

## Debugging a failing test

1. **Read the failure summary** in pytest output — Playwright assertions print the actual locator and what it saw.
2. **Open the Allure attachment** — every failure has a screenshot, video, and trace.
3. **Open the Playwright trace** — interactive timeline, network, console, DOM snapshots:
   ```bash
   playwright show-trace reports/trace-<test-name>.zip
   ```
4. **Re-run with full visibility**:
   ```bash
   HEADLESS=false SLOW_MO=500 pytest -k "<test name>" -s --tb=long
   ```
5. **Check logs** in `reports/logs/` for the DEBUG breadcrumb trail.

---

## Quality gates before committing

```bash
ruff check src tests config       # lint
black src tests config            # format
mypy src                          # types
pytest -m smoke -n auto           # smoke
```

CI runs the same checks, but a 30-second local run avoids the embarrassing "fix lint" follow-up commit.
