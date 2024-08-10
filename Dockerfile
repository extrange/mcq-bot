FROM python:3.12-slim AS base

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl=7.88.1-10+deb12u6 && \
    rm -rf /var/lib/apt/lists/*

# trufflehog: secret scanning
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /usr/local/bin

FROM base as test

# Your test actions here
