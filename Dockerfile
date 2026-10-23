FROM python:3.14-slim@sha256:caaf356f40667c496d405780745b9ac25771c189a51dfcc42430d531ea09f8a2

COPY --from=ghcr.io/astral-sh/uv:latest@sha256:3adc3706091ce7c2fe595e669628caedd6d951551b92b258b7e7dbe06d9440bc /uv /uvx /bin/

ENV TZ=Europe/Amsterdam \
    PIP_ROOT_USER_ACTION=ignore \
    PYTHONPATH=/app/src

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates fonts-liberation \
    libgtk-3-0 libx11-xcb1 libasound2 libdbus-glib-1-2 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Third-party deps only — stable across a version-only release
COPY requirements.txt requirements.txt
RUN uv venv .venv \
    && uv pip install --python .venv/bin/python -r requirements.txt

# Download the Camoufox (Firefox) browser for the build's architecture.
# Depends only on camoufox already being installed above — also stable.
# Build this image for the same arch it will run on (linux/arm64 for the Pi).
RUN .venv/bin/python -m camoufox fetch

# These DO change every release, but installing your own package on top
# of an already-populated venv is fast — no network calls needed
COPY pyproject.toml uv.lock ./
COPY src /app/src
RUN uv sync --frozen --no-cache

CMD ["/app/.venv/bin/fastapi", "run", "src/auction_rss_api/main.py", "--port", "80", "--host", "0.0.0.0"]