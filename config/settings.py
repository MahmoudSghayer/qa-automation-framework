"""
Centralized settings loader.

Resolution order (highest priority wins):
    1. Environment variables (e.g. BROWSER=firefox)
    2. YAML file for the active environment (config/<env>.yaml)
    3. Hard-coded defaults below

Why a singleton class instead of a global dict:
    - Type-safe attribute access (Settings.app.base_url) catches typos at lint time
    - One construction point makes it trivial to mock in unit tests
    - Lazy load = no I/O cost when only a subset is used
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

# Load .env once at import time. Safe — load_dotenv is idempotent.
load_dotenv()

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


@dataclass(frozen=True)
class AppConfig:
    base_url: str
    api_base_url: str


@dataclass(frozen=True)
class BrowserConfig:
    default: str
    headless: bool
    viewport_width: int
    viewport_height: int
    timeout_ms: int
    navigation_timeout_ms: int
    video: str
    screenshot: str
    trace: str


@dataclass(frozen=True)
class ApiConfig:
    timeout_seconds: int
    retries: int


@dataclass(frozen=True)
class DatabaseConfig:
    enabled: bool
    host: str
    port: int
    name: str
    user: str
    password: str
    pool_size: int
    read_only: bool = False


@dataclass(frozen=True)
class Credentials:
    username: str
    password: str


@dataclass(frozen=True)
class Settings:
    environment: str
    app: AppConfig
    browser: BrowserConfig
    api: ApiConfig
    database: DatabaseConfig
    credentials: Credentials
    workers: str = "auto"


def _load_yaml(env: str) -> dict[str, Any]:
    path = CONFIG_DIR / f"{env}.yaml"
    if not path.exists():
        raise FileNotFoundError(
            f"Config file not found: {path}. "
            f"Available: {[p.name for p in CONFIG_DIR.glob('*.yaml')]}"
        )
    with path.open() as f:
        return yaml.safe_load(f) or {}


def _bool(value: Any, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Build Settings once per process. Re-import does not reload."""
    env = os.getenv("TEST_ENV", "staging").lower()
    raw = _load_yaml(env)

    app_raw = raw.get("app", {})
    br_raw = raw.get("browser", {})
    vp = br_raw.get("viewport", {}) or {}
    api_raw = raw.get("api", {})
    db_raw = raw.get("database", {})

    return Settings(
        environment=raw.get("environment", env),
        app=AppConfig(
            base_url=os.getenv("BASE_URL", app_raw.get("base_url", "")),
            api_base_url=os.getenv("API_BASE_URL", app_raw.get("api_base_url", "")),
        ),
        browser=BrowserConfig(
            default=os.getenv("BROWSER", br_raw.get("default", "chromium")),
            headless=_bool(os.getenv("HEADLESS"), br_raw.get("headless", True)),
            viewport_width=int(vp.get("width", 1920)),
            viewport_height=int(vp.get("height", 1080)),
            timeout_ms=int(br_raw.get("timeout_ms", 30000)),
            navigation_timeout_ms=int(br_raw.get("navigation_timeout_ms", 45000)),
            video=br_raw.get("video", "retain-on-failure"),
            screenshot=br_raw.get("screenshot", "only-on-failure"),
            trace=br_raw.get("trace", "retain-on-failure"),
        ),
        api=ApiConfig(
            timeout_seconds=int(api_raw.get("timeout_seconds", 15)),
            retries=int(api_raw.get("retries", 2)),
        ),
        database=DatabaseConfig(
            enabled=_bool(db_raw.get("enabled"), False),
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            name=os.getenv("DB_NAME", ""),
            user=os.getenv("DB_USER", ""),
            password=os.getenv("DB_PASSWORD", ""),
            pool_size=int(db_raw.get("pool_size", 5)),
            read_only=_bool(db_raw.get("read_only"), False),
        ),
        credentials=Credentials(
            username=os.getenv("ORANGEHRM_USERNAME", "Admin"),
            password=os.getenv("ORANGEHRM_PASSWORD", "admin123"),
        ),
        workers=os.getenv("PYTEST_WORKERS", "auto"),
    )


# Convenience export so tests can do: from config.settings import settings
settings = get_settings()
