# QA Automation Framework — Python · Playwright · Pytest

[![CI](https://github.com/<MahmoudSghayer>/qa-automation-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/<MahmoudSghayer>/qa-automation-framework/actions/workflows/ci.yml)
[![Allure Report](https://img.shields.io/badge/Allure-report-success?logo=qameta)](https://<MahmoudSghayer>.github.io/qa-automation-framework/)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue?logo=python)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.47-2EAD33?logo=playwright)](https://playwright.dev/python/)
[![Pytest](https://img.shields.io/badge/Pytest-8.3-blue?logo=pytest)](https://docs.pytest.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A production-grade end-to-end test automation framework demonstrating real-world QA architecture patterns:
**UI + API + Database** validation against [OrangeHRM Demo](https://opensource-demo.orangehrmlive.com),
with full CI/CD, parallel execution, Dockerization, and Allure reporting.

> Built to mirror what enterprise QA teams ship — not a tutorial repo.

---

## 🎯 Highlights

- **Three-layer testing**: UI (Playwright) · API (requests + Pydantic) · DB (SQLAlchemy)
- **Page Object Model** with a single `BasePage` mediating every Playwright call
- **Data-driven tests** via JSON fixtures + Faker
- **Parallel execution** with `pytest-xdist` (`-n auto`)
- **Auto-retry on flake** with `pytest-rerunfailures`
- **Failure forensics**: screenshot + video + Playwright trace, all attached to Allure
- **Multi-environment**: `dev` / `staging` / `prod` via YAML + env vars (12-Factor)
- **CI/CD**: GitHub Actions matrix (Chromium + Firefox), nightly regression, Allure published to GitHub Pages
- **Dockerized**: identical execution locally and in CI

---

## 📦 Tech Stack

| Layer | Tool |
|---|---|
| Language | Python 3.12 |
| Browser automation | Playwright |
| Test runner | Pytest |
| API client | `requests` + Pydantic |
| Database | SQLAlchemy + PyMySQL |
| Reporting | Allure + pytest-html |
| Logging | Loguru |
| Config | YAML + python-dotenv |
| CI/CD | GitHub Actions |
| Containers | Docker + docker-compose |
| Code quality | Ruff + Black + Mypy |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│  tests/   ←  feature-grouped, layer-grouped, no logic  │
├─────────────────────────────────────────────────────────┤
│  pages/        api/clients/        db/queries/         │
│       ↓             ↓                    ↓             │
├─────────────────────────────────────────────────────────┤
│  src/core/  ← BasePage, exceptions, framework primitives│
├─────────────────────────────────────────────────────────┤
│  config/   utils/  ← cross-cutting (settings, logger)  │
└─────────────────────────────────────────────────────────┘
```

Dependencies flow one direction. Tests depend on pages, pages depend on core, core depends on config — never the reverse. New test engineers add tests without touching `core/`.

See **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** for a deep dive.

---

## 📁 Project Structure

```
qa-automation-framework/
├── .github/workflows/        # GitHub Actions pipelines
│   ├── ci.yml                #   main CI: lint → smoke → regression → publish
│   └── docker.yml            #   dockerized run
├── config/                   # environment configuration
│   ├── settings.py           #   typed Settings loader (yaml + env vars)
│   ├── dev.yaml
│   ├── staging.yaml
│   └── prod.yaml
├── src/
│   ├── core/                 # framework primitives
│   │   ├── base_page.py      #   single integration point with Playwright
│   │   └── exceptions.py
│   ├── pages/                # page objects (one per page)
│   │   ├── login_page.py
│   │   ├── dashboard_page.py
│   │   └── pim_page.py
│   ├── api/
│   │   ├── clients/          #   resource-based HTTP clients
│   │   │   ├── base_client.py
│   │   │   ├── auth_client.py
│   │   │   └── employee_client.py
│   │   └── models/           #   Pydantic request/response models
│   ├── db/                   # database layer
│   │   ├── db_client.py      #   SQLAlchemy engine wrapper
│   │   └── queries.py        #   centralized SQL
│   └── utils/                # cross-cutting helpers
│       ├── logger.py         #   loguru-based, per-worker safe
│       ├── data_factory.py   #   Faker-powered test data
│       └── file_loader.py
├── tests/
│   ├── ui/                   # Playwright tests
│   │   ├── login/
│   │   ├── employees/
│   │   └── leave/
│   ├── api/                  # pure API tests
│   ├── integration/          # UI + API + DB end-to-end
│   └── data/                 # JSON/YAML fixtures
├── reports/                  # generated artifacts (gitignored)
│   ├── allure-results/
│   ├── screenshots/
│   ├── videos/
│   └── logs/
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── scripts/
│   ├── run-tests.sh
│   └── generate-report.sh
├── docs/
│   ├── ARCHITECTURE.md
│   ├── EXECUTION.md
│   └── diagrams/
├── conftest.py               # root fixtures + hooks
├── pytest.ini
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Git
- (Optional) Docker 24+ for containerized runs
- (Optional) [Allure CLI](https://allurereport.org/docs/install/) for HTML reports

### Local install (3 commands)

```bash
git clone https://github.com/MahmoudSghayer/qa-automation-framework.git
cd qa-automation-framework

python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install --with-deps chromium

cp .env.example .env                                  # then edit credentials
```

### Run tests

```bash
# Smoke suite, parallel, all browsers headless
pytest -m smoke -n auto

# Single feature, headed (visible browser) for debugging
HEADLESS=false pytest tests/ui/login -v

# Full regression, retry flaky tests up to 2x
pytest -m regression --reruns 2 --reruns-delay 1

# API-only (fast)
pytest -m api

# Run on a different env
TEST_ENV=dev pytest -m smoke
```

### View Allure report

```bash
./scripts/generate-report.sh
# opens at http://localhost:port-served-by-allure
```

### Docker

```bash
docker compose -f docker/docker-compose.yml up --build tests
docker compose -f docker/docker-compose.yml up allure       # → http://localhost:5050
```

---

## 🏷️ Test Markers

| Marker | Purpose | When it runs |
|---|---|---|
| `smoke` | Critical path | Every PR |
| `regression` | Full coverage | Nightly + on-demand |
| `ui` / `api` / `integration` | Layer | Auto-applied by directory |
| `auth` / `crud` / `negative` | Feature category | Manual filtering |
| `slow` | >30s tests | Excluded from smoke |

Combine with boolean expressions: `pytest -m "smoke and not slow"`.

---

## 🧪 What's Tested

| Area | UI | API | DB |
|---|:---:|:---:|:---:|
| Login (valid/invalid/empty/edge) | ✅ | ✅ | — |
| Session persistence + logout | ✅ | — | — |
| Employee search (positive + negative) | ✅ | ✅ | — |
| Employee CRUD | ✅ | ✅ | ✅ |
| Form validation | ✅ | ✅ | — |
| End-to-end consistency (UI ⇄ API ⇄ DB) | — | — | ✅ (integration) |

---

## 🔁 CI/CD

Every push & PR triggers:

1. **Lint** (Ruff + Black) — fail fast on style issues
2. **Smoke** — Chromium + Firefox in parallel matrix
3. **Allure publish** to GitHub Pages on `main`

Nightly cron triggers full **regression**. Manual `workflow_dispatch` lets QA run any marker against any env.

Failures upload screenshots, videos, and traces as workflow artifacts (14-day retention).

---

## 🧠 Why this framework scales

- **One direction of dependency**: tests → pages → core → config
- **`BasePage` chokepoint**: Playwright API drift is a one-file fix
- **Centralized SQL** in `queries.py`: DBA reviews one file
- **Pydantic models**: API contract changes fail at parse time, not assertion time
- **Auto-marking by directory**: writing a test in `tests/ui/` means it's a UI test — no boilerplate
- **Settings as a frozen dataclass**: typos caught by linters, not runtime

---

## 🗺️ Roadmap

- [ ] Visual regression with Playwright snapshots
- [ ] Performance smoke (response-time SLOs)
- [ ] Mobile viewports via Playwright device emulation
- [ ] Accessibility checks (axe-playwright)
- [ ] Test impact analysis (run only tests affected by code change)
- [ ] BDD layer (pytest-bdd) for stakeholder-readable scenarios

---

## 📚 Further Reading

- [Architecture deep dive](docs/ARCHITECTURE.md)
- [Execution guide](docs/EXECUTION.md)
- [Contribution guide](docs/CONTRIBUTING.md)

---

## 📜 License

MIT. See [LICENSE](LICENSE).

## 👤 Author

**Mahmoud Sghayer** — [LinkedIn](https://linkedin.com/in/ma7muds) · [GitHub](https://github.com/MahmoudSghayer)

> Built as a portfolio project to demonstrate enterprise QA practices. Reach out — happy to walk through any part of it.
