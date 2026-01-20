FROM python@sha256:9b81fe9acff79e61affb44aaf3b6ff234392e8ca477cb86c9f7fd11732ce9b6a

# Install UV
COPY --from=ghcr.io/astral-sh/uv@sha256:eed5b30f303a09933451248c6ccde9f53e922a4e5d80bde560ab38662ce6ccf5 /uv /uvx /bin/

# Set timezone
ENV TZ=Europe/Amsterdam

# Ignore pip root error warnings
ENV PIP_ROOT_USER_ACTION=ignore

# Deploy code
WORKDIR /app
COPY requirements.txt requirements.txt
RUN --mount=type=cache,target=/root/.cache \
    uv pip install --system -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--no-access-log"]