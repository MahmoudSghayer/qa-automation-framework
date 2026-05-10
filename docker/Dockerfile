# ============================================================
# Production-grade test runner image
#
# Why mcr.microsoft.com/playwright/python:
#   - Pre-installed Chromium/Firefox/WebKit + system deps
#   - Trusted by Microsoft, versioned to match Playwright
#   - Saves ~3 minutes per CI run vs. installing from scratch
# ============================================================
FROM mcr.microsoft.com/playwright/python:v1.47.0-jammy

# Reproducible, predictable Python behavior in containers
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

WORKDIR /app

# Layer 1: install deps first → docker layer cache survives source edits
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Layer 2: project source
COPY . .

# Generated dirs (ignored by .dockerignore otherwise)
# Create non-root user first
RUN useradd -m -u 1001 qauser

# Create writable output dirs and give qauser ownership of everything in /app
RUN mkdir -p /app/reports/allure-results \
             /app/reports/screenshots \
             /app/reports/videos \
             /app/reports/logs \
    && chown -R qauser:qauser /app

USER qauser

# Default command runs smoke; override with `docker run ... pytest -m regression`
CMD ["pytest", "-m", "smoke", "-n", "auto"]
