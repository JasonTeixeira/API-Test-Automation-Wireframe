# API Test Automation Framework

[![CI/CD](https://github.com/JasonTeixeira/API-Test-Automation-Wireframe/actions/workflows/api-tests.yml/badge.svg)](https://github.com/JasonTeixeira/API-Test-Automation-Wireframe/actions/workflows/api-tests.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An API testing framework I built to test REST APIs properly. Built with Python + Pytest + Requests, featuring 125+ tests, retry logic, Pydantic validation, and a complete CI/CD pipeline.

```
╔══════════════════════════════════════════════════════════════╗
║                  WHAT I ACTUALLY BUILT                       ║
╠══════════════════════════════════════════════════════════════╣
║  125+ Tests        CRUD, auth, workflows, edge cases         ║
║  Client Layer      Retry logic, logging, session mgmt        ║
║  Pydantic Models   Type-safe validation for all responses    ║
║  CI/CD Pipeline    9 jobs, parallel execution, coverage      ║
║  Docker Support    Multi-stage builds, 6 execution modes     ║
║  Security Tests    SQL injection, XSS, vulnerability scans   ║
║  Performance       Response time tracking & assertions       ║
║  Real Coverage     >80% code coverage on 3,500+ LOC          ║
╚══════════════════════════════════════════════════════════════╝
```

## Why This Exists

I wanted to build a proper API testing framework—not just a pile of `requests.get()` calls thrown into test files. This framework treats API clients like first-class citizens with retry logic, proper logging, and response tracking.

I used the [ReqRes API](https://reqres.in) as the test target because it's stable and covers common REST patterns (users, resources, auth). The framework itself is what matters here—it's built to scale.

## Test Breakdown

```
┌──────────────────────────────────────────────────────────────┐
│  Test Suite          Tests   What They Cover                 │
├──────────────────────────────────────────────────────────────┤
│  Users API            35     GET/POST/PUT/PATCH/DELETE       │
│                               Pagination, filters, sorting   │
│                               Schema validation, performance │
│                                                              │
│  Resources API        28     Full CRUD operations            │
│                               Data integrity checks          │
│                               Error handling scenarios       │
│                                                              │
│  Authentication       28     Login/register flows            │
│                               Token management               │
│                               Security edge cases            │
│                                                              │
│  Workflows            11     Multi-step E2E scenarios        │
│                               User journeys across endpoints │
│                                                              │
│  Negative/Edge        23     Invalid inputs, SQL injection   │
│                               XSS attempts, boundary values  │
├──────────────────────────────────────────────────────────────┤
│  TOTAL                125+   Real coverage across the board  │
└──────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- pip
- Docker (optional)

### Installation

```bash
git clone https://github.com/JasonTeixeira/API-Test-Automation-Wireframe.git
cd API-Test-Automation-Wireframe

python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

pip install -r requirements.txt
cp .env.example .env
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# Smoke tests (fast feedback, ~30s)
pytest tests/ -m smoke -v

# Specific suite
pytest tests/users/ -v

# With coverage
pytest tests/ --cov=clients --cov=models --cov=utils --cov=config

# Parallel (4 workers)
pytest tests/ -n 4 -v

# HTML report
pytest tests/ --html=reports/report.html --self-contained-html

# Allure report
pytest tests/ --alluredir=reports/allure-results
allure serve reports/allure-results
```

### Docker

```bash
# Full suite
docker-compose --profile full up test-runner

# Smoke only
docker-compose --profile smoke up smoke-tests

# Specific suite
docker-compose --profile users up users-tests

# Parallel
docker-compose --profile parallel up parallel-tests
```

## Project Structure

```
API-Test-Automation-Wireframe/
├── .github/
│   └── workflows/
│       └── api-tests.yml          # CI/CD pipeline (364 lines)
├── clients/
│   ├── base_client.py             # Base HTTP client (356 lines)
│   ├── users_client.py            # Users API client (145 lines)
│   ├── resources_client.py        # Resources API client (128 lines)
│   └── auth_client.py             # Authentication client (130 lines)
├── models/
│   └── schemas.py                 # Pydantic models (316 lines)
├── utils/
│   ├── logger.py                  # Custom logger (195 lines)
│   └── test_data.py               # Test data generators (279 lines)
├── config/
│   └── settings.py                # Settings management (137 lines)
├── tests/
│   ├── users/                     # 35 user API tests (347 lines)
│   ├── resources/                 # 28 resource API tests (309 lines)
│   ├── auth/                      # 28 authentication tests (285 lines)
│   ├── workflows/                 # 11 E2E workflow tests (187 lines)
│   └── negative/                  # 23 negative tests (263 lines)
├── conftest.py                    # Fixtures & config (513 lines)
├── requirements.txt               # Python dependencies
├── pyproject.toml                 # Project configuration
├── Dockerfile                     # Multi-stage Docker build
├── docker-compose.yml             # Docker orchestration
└── README.md                      # This file
```

**Total Lines of Code: 3,500+**

## Architecture

Built around 3 layers:

```
   Test Layer (125+ tests)           pytest fixtures + markers
        │
        v
   Client Layer                      retry, logging, sessions
   ├── BaseClient
   ├── UsersClient
   ├── ResourcesClient
   └── AuthClient
        │
        v
   Model Layer (Pydantic)            type-safe validation
   ├── User, UserList
   ├── Resource, ResourceList
   └── LoginRequest, LoginResponse
        │
        v
   HTTP Layer (Requests)             actual network calls
        │
        v
   ReqRes API
```

### Client Layer

All clients inherit from BaseClient, which handles:
- Automatic retry on 429 / 5xx (exponential backoff)
- Request/response logging (sanitizes tokens)
- Session pooling for speed
- Response time tracking

```python path=null start=null
from clients.users_client import UsersClient

client = UsersClient()
response = client.get_users(page=1, per_page=10)

assert response.is_success()
assert response.status_code == 200
assert response.elapsed_time < 1.0
```

### Model Layer

Pydantic models validate every response and make the tests readable:

```python path=null start=null
from models.schemas import User, validate_user_schema

user = User(**response_data)  # auto-validates types, fields
validated = validate_user_schema(response_data)  # JSON Schema
```

### Test Layer

Tests use markers (`@pytest.mark.smoke`, `@pytest.mark.users`) so you can run subsets:

```python path=null start=null
@pytest.mark.users
@pytest.mark.smoke
def test_get_user(users_client, existing_user_id):
    response = users_client.get_user(existing_user_id)
    assert response.is_success()
    assert response.json["data"]["id"] == existing_user_id
```

## Test Markers

Run subsets by marker:

```bash
pytest -m smoke        # Critical path (~20 tests, ~30s)
pytest -m regression   # Full suite (125+ tests)
pytest -m users        # User API tests
pytest -m resources    # Resource API tests
pytest -m auth         # Authentication tests
pytest -m workflows    # E2E workflows
pytest -m security     # Security tests (SQL injection, XSS)
pytest -m performance  # Performance assertions
pytest -m negative     # Negative/edge cases
```

## CI/CD Pipeline

9 jobs in GitHub Actions:

1. Code Quality: black, isort, pylint, mypy
2. Smoke Tests: fast feedback loop (~30s)
3. Test Matrix: 5 parallel jobs (users, resources, auth, workflows, negative)
4. Parallel Execution: full suite with 4 workers
5. Coverage Gate: enforces >80% threshold
6. Allure Reports: auto-published to GitHub Pages
7. Regression Suite: daily scheduled runs
8. Security Tests: SQL injection, XSS, etc.
9. Notifications: Slack/email summary on failures

Smoke runs first. If it passes, the full suite fires in parallel. Coverage check is last so you don't block on it unless everything else passes.

## Docker

6 profiles for different execution modes:

```bash
docker-compose --profile full up test-runner       # Full suite
docker-compose --profile smoke up smoke-tests      # Smoke only
docker-compose --profile users up users-tests      # Users suite
docker-compose --profile resources up resources-tests
docker-compose --profile auth up auth-tests
docker-compose --profile parallel up parallel-tests  # 4 workers
```

Multi-stage Dockerfile:
- Base: Python 3.11 slim
- Dependencies: Cached pip installs
- Test Runner: Complete test environment
- Specialized images per suite

## Reporting

### HTML Reports

```bash
pytest tests/ --html=reports/report.html --self-contained-html
open reports/report.html
```

Self-contained, includes:
- Pass/fail status
- Execution times
- Error traces

### Allure Reports

```bash
pytest tests/ --alluredir=reports/allure-results
allure serve reports/allure-results
```

Provides:
- Test execution timeline
- Historical trends
- Failure analysis
- Request/response bodies
- Test categories

### Code Coverage

```bash
pytest tests/ --cov=clients --cov=models --cov=utils --cov=config \\
  --cov-report=html --cov-report=term

open htmlcov/index.html
```

Target: >80%

## Configuration

### Environment Variables

Set via `.env` file:

```bash
API_BASE_URL=https://reqres.in/api
API_TIMEOUT=30
API_RETRY_COUNT=3
PARALLEL_WORKERS=4
LOG_LEVEL=INFO
PERFORMANCE_THRESHOLD_MS=1000
```

### Pydantic Settings

Type-safe config in `config/settings.py`:

```python path=null start=null
from config.settings import settings

settings.api_base_url      # https://reqres.in/api
settings.api_timeout       # 30
settings.parallel_workers  # 4
```

## Development

### Code Quality

```bash
# Format
black .
isort .

# Lint
pylint clients/ models/ utils/ config/

# Type check
mypy clients/ models/ utils/ config/
```

### Adding Tests

1. Create test file in appropriate directory
2. Use fixtures from `conftest.py`
3. Add pytest markers (`@pytest.mark.smoke`, `@pytest.mark.users`, etc.)
4. Follow AAA pattern (Arrange-Act-Assert)
5. Include docstrings

## What was hard (and how I fixed it)

- Flaky external API responses (429s, occasional 5xx): added retry with exponential backoff on specific status codes and timeouts. Tuned defaults so tests stay fast but resilient.
- Logs leaking tokens: wrote a sanitizer that redacts known secrets before logging request/response bodies.
- Parallel runs stepping on each other: kept tests stateless and generated unique data per run; isolated any cross-test state behind fixtures.
- Schema drift: locked response validation behind Pydantic models + JSON Schema so breaking changes are obvious.

## Decisions I made

- Python + Pytest + Requests over heavier frameworks: I wanted full control and simple primitives.
- Pydantic for type-safety and fast feedback on bad payloads.
- Tenacity-style retry semantics (exponential backoff) rather than rolling my own.
- Keep CI fast: smoke first, then parallelize the rest. Coverage is enforced but not at the cost of developer velocity.

## If you only have 5 minutes

- Run smoke tests: `pytest -m smoke -v`
- Full suite, parallel: `pytest -n 4 -v`
- HTML report: `pytest --html=reports/report.html --self-contained-html`
- Allure: `pytest --alluredir=reports/allure-results && allure serve reports/allure-results`

## Roadmap / Next

- Contract tests per endpoint version (pin schemas by version)
- More negative and chaos scenarios (timeouts, malformed JSON)
- Toggleable network stubbing layer for local dev speed
- K6/Locust performance profiles wired into CI (threshold gates)

## Docs

- Architecture: docs/API_ARCHITECTURE.md
- Build Story: JOURNEY.md

## License

MIT — see LICENSE.
