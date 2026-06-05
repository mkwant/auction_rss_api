FROM python:3.14-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set timezone
ENV TZ=Europe/Amsterdam
ENV PIP_ROOT_USER_ACTION=ignore
ENV PYTHONPATH=/app/src
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=1

WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl ca-certificates fonts-liberation libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 \
    libgbm1 libasound2 libpangocairo-1.0-0 libpango-1.0-0 libgtk-3-0 \
    libxcb1 libx11-xcb1 libxshmfence1 libxrender1 libxext6 xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock
RUN --mount=type=cache,target=/root/.cache/pip \
    uv sync --frozen --no-cache

# Copy the application
COPY src /app/src

# Install Playwright browsers
RUN python -m playwright install chromium

# Run the app
CMD ["/app/.venv/bin/fastapi", "run", "src/auction_rss_api/main.py", "--port", "80", "--host", "0.0.0.0"]