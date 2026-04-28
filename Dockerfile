FROM python:3.14-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set timezone
ENV TZ=Europe/Amsterdam
ENV PIP_ROOT_USER_ACTION=ignore
ENV PYTHONPATH=/app/src

# Set workdir
WORKDIR /app

# Install the application dependencies.
COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock
RUN --mount=type=cache,target=/root/.cache/pip \
    uv sync --frozen --no-cache

# Copy the application into the container.
COPY src /app/src

# Run the application.
CMD ["/app/.venv/bin/fastapi", "run", "src/auction_rss_api/main.py", "--port", "80", "--host", "0.0.0.0"]