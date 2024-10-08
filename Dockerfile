FROM python:3.12-slim AS base

ENV POETRY_VERSION=1.8.3
ENV TZ=Asia/Singapore

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl && \
    rm -rf /var/lib/apt/lists/*

#-------------------

FROM base AS dev

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    sqlite3

# trufflehog: secret scanning
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /usr/local/bin

#-------------------

FROM base AS builder

RUN pip install --no-cache-dir poetry=="$POETRY_VERSION"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY poetry.lock pyproject.toml ./

RUN --mount=type=cache,target=${POETRY_CACHE_DIR} \
    poetry install --without=dev --no-root

#--------------------

FROM base AS deployment

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app/src

RUN useradd -ms /bin/bash 1000

USER 1000

# Copy virtual environment from builder
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY . /app

CMD ["python", "-m", "mcq_bot.main"]
