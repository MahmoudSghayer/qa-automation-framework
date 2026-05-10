# Architecture Diagrams

GitHub renders Mermaid blocks natively, so these show up as real diagrams in the rendered Markdown.

## 1. Layered architecture & dependency flow

```mermaid
graph TD
    subgraph TestLayer["🧪 Test Layer"]
        T1["tests/ui/<br/>login • employees • leave"]
        T2["tests/api/<br/>employees_api"]
        T3["tests/integration/<br/>UI ⇄ API ⇄ DB"]
    end

    subgraph DomainLayer["📦 Domain Layer"]
        P["src/pages/<br/>LoginPage • PimPage • LeavePage"]
        A["src/api/clients/<br/>AuthClient • EmployeeClient"]
        D["src/db/<br/>EmployeeQueries"]
    end

    subgraph CoreLayer["⚙️ Core Layer"]
        BP["src/core/base_page.py<br/>(only file that imports Playwright)"]
        BC["src/api/clients/base_client.py<br/>(only file that imports requests)"]
        DC["src/db/db_client.py<br/>(only file that imports SQLAlchemy)"]
        EX["src/core/exceptions.py"]
    end

    subgraph CrossCutting["🔧 Cross-cutting"]
        CFG["config/settings.py<br/>(YAML + env vars)"]
        LOG["src/utils/logger.py<br/>(loguru, xdist-safe)"]
        UTIL["src/utils/<br/>data_factory • file_loader"]
    end

    T1 --> P
    T2 --> A
    T3 --> P
    T3 --> A
    T3 --> D

    P --> BP
    A --> BC
    D --> DC

    BP --> EX
    BC --> EX
    DC --> EX

    BP --> CFG
    BC --> CFG
    DC --> CFG

    BP -.uses.-> LOG
    BC -.uses.-> LOG
    DC -.uses.-> LOG

    P -.uses.-> UTIL
    A -.uses.-> UTIL

    style TestLayer fill:#e3f2fd,stroke:#1976d2
    style DomainLayer fill:#f3e5f5,stroke:#7b1fa2
    style CoreLayer fill:#fff3e0,stroke:#f57c00
    style CrossCutting fill:#e8f5e9,stroke:#388e3c
```

**Reading the diagram:** dependencies flow downward only. A test never imports another test, a page object never imports a test, core never imports a page object. This one rule is what makes the framework refactor-friendly at scale.

---

## 2. Test execution lifecycle

```mermaid
sequenceDiagram
    participant CI as GitHub Actions
    participant PT as pytest
    participant CF as conftest.py
    participant FX as Fixtures
    participant T as Test
    participant PG as PageObject
    participant API as ApiClient
    participant AL as Allure

    CI->>PT: pytest -m smoke -n auto
    PT->>CF: collect & configure
    CF->>CF: log env / browser / workers
    PT->>FX: build session fixtures (browser, auth_client)
    FX->>API: AuthClient.login() → cookie cached
    Note over PT,T: per-test loop
    PT->>FX: build context + page (fresh)
    PT->>T: run test
    T->>PG: page-object method
    PG->>PG: BasePage.click/fill/assert
    alt test passes
        T->>PT: ✅
    else test fails
        T->>CF: pytest_runtest_makereport hook
        CF->>FX: capture screenshot + trace
        FX->>AL: attach all artifacts
    end
    PT->>FX: teardown context (close, video saved)
    PT->>CI: report + artifacts
    CI->>AL: publish report to GitHub Pages
```

---

## 3. CI/CD pipeline

```mermaid
flowchart LR
    DEV[Developer push / PR] --> LINT
    SCH[Nightly cron 02:00 UTC] --> REG[Regression suite]
    DISP[workflow_dispatch] --> CHOICE{marker?}

    LINT[🔍 Lint<br/>Ruff + Black] --> SMOKE
    SMOKE[💨 Smoke<br/>Chromium + Firefox<br/>matrix, parallel] --> ART[📦 Upload artifacts<br/>screenshots, videos, traces]
    SMOKE --> ALLURE[📊 Allure<br/>publish to gh-pages]

    REG --> ART
    REG --> ALLURE

    CHOICE -->|smoke| SMOKE
    CHOICE -->|regression| REG
    CHOICE -->|api| API_RUN[API-only run]

    style LINT fill:#fff3e0
    style SMOKE fill:#e3f2fd
    style REG fill:#f3e5f5
    style ALLURE fill:#e8f5e9
```
