FROM python@sha256:9b81fe9acff79e61affb44aaf3b6ff234392e8ca477cb86c9f7fd11732ce9b6a

# Install UV
COPY --from=ghcr.io/astral-sh/uv@sha256:ac4baed46b4ca69acf99fe645563970b758fecab89ad48d8222356d68dd06e7b /uv /uvx /bin/

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