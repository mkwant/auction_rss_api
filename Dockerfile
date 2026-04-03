FROM python@sha256:5e2dbd4bbdd9c0e67412aea9463906f74a22c60f89eb7b5bbb7d45b66a2b68a6 AS base

# Install UV
COPY --from=ghcr.io/astral-sh/uv@sha256:87a04222b228501907f487b338ca6fc1514a93369bfce6930eb06c8d576e58a4 /uv /uvx /bin/

# Set timezone
ENV TZ=Europe/Amsterdam
ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /app

# Install dependencies with cache
COPY requirements.txt requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    uv pip install --system -r requirements.txt

# Copy application code
COPY src /app/src

CMD ["uvicorn", "auction_rss_api.main:app", "--host", "0.0.0.0", "--port", "80", "--no-access-log"]
