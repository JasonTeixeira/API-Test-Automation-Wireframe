# Multi-stage build for API test automation

# Stage 1: Base image with Python
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Dependencies
FROM base as dependencies

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Stage 3: Test runner
FROM dependencies as test-runner

# Copy application code
COPY . .

# Create reports directory
RUN mkdir -p reports/html reports/allure-results reports/coverage logs

# Set Python path
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('https://reqres.in/api/users/1')" || exit 1

# Default command - run all tests
CMD ["pytest", "tests/", "-v", "--html=reports/html/report.html", "--self-contained-html"]

# Stage 4: Smoke tests
FROM test-runner as smoke-tests
CMD ["pytest", "tests/", "-m", "smoke", "-v"]

# Stage 5: Specific test suites
FROM test-runner as users-tests
CMD ["pytest", "tests/users/", "-v"]

FROM test-runner as resources-tests
CMD ["pytest", "tests/resources/", "-v"]

FROM test-runner as auth-tests
CMD ["pytest", "tests/auth/", "-v"]
