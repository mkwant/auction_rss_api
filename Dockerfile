FROM python:3.12-slim

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set timezone
ENV TZ=Europe/Amsterdam

# Ignore pip root error warnings
ENV PIP_ROOT_USER_ACTION=ignore

# Update apt-get
RUN apt-get update

# Deploy code
WORKDIR /app
COPY requirements.txt requirements.txt
RUN uv pip install --system -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--no-access-log"]