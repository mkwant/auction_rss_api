FROM python@sha256:5e2dbd4bbdd9c0e67412aea9463906f74a22c60f89eb7b5bbb7d45b66a2b68a6

# Install UV
COPY --from=ghcr.io/astral-sh/uv@sha256:87a04222b228501907f487b338ca6fc1514a93369bfce6930eb06c8d576e58a4 /uv /uvx /bin/

# Set timezone
ENV TZ=Europe/Amsterdam

# Ignore pip root error warnings
ENV PIP_ROOT_USER_ACTION=ignore

# Deploy code
WORKDIR /app
COPY requirements.txt requirements.txt
RUN uv pip install --system -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--no-access-log"]