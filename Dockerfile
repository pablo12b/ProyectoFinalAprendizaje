# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# Prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Install system dependencies
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Setup work directory
WORKDIR $PYSETUP_PATH

# Copy project dependencies configuration
COPY pyproject.toml poetry.lock ./

# Install runtime dependencies
RUN poetry install --no-root --only main

# Copy application code
WORKDIR /app
COPY business_backend ./business_backend
COPY README.md .

# Create a non-root user and switch to it
RUN addgroup --system --gid 1001 appgroup \
    && adduser --system --uid 1001 --ingroup appgroup --home /home/appuser appuser
USER appuser

# Expose the port (Cloud Run sets PORT env var)
ENV PORT=8080
EXPOSE $PORT

# Run the application
# We use the factory pattern as defined in main.py
CMD exec uvicorn business_backend.main:create_business_backend_app --host 0.0.0.0 --port ${PORT} --factory
