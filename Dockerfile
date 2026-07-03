FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV TZ=Europe/Amsterdam \
    PIP_ROOT_USER_ACTION=ignore \
    PYTHONPATH=/app/src \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl ca-certificates fonts-liberation libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 \
    libgbm1 libasound2 libpangocairo-1.0-0 libpango-1.0-0 libgtk-3-0 \
    libxcb1 libx11-xcb1 libxshmfence1 libxrender1 libxext6 xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Third-party deps only — stable across a version-only release
COPY requirements.txt requirements.txt
RUN uv venv .venv \
    && uv pip install --python .venv/bin/python -r requirements.txt

# Depends only on playwright already being installed above — also stable
RUN .venv/bin/python -m playwright install chromium

# These DO change every release, but installing your own package on top
# of an already-populated venv is fast — no network calls needed
COPY pyproject.toml uv.lock ./
COPY src /app/src
RUN uv sync --frozen --no-cache

CMD ["/app/.venv/bin/fastapi", "run", "src/auction_rss_api/main.py", "--port", "80", "--host", "0.0.0.0"]