# API Test Framework: Build Journey

## Why I Built This

I wanted to build a proper API testing framework from scratch—not just a pile of `requests.get()` calls scattered across test files. This project was about treating API clients as first-class citizens with retry logic, proper error handling, and structured logging.

I used the [ReqRes API](https://reqres.in) as the test target. It's stable, publicly available, and covers common REST patterns (users, resources, auth). The framework itself is what matters here—it's built to scale beyond this one API.

---

## Timeline

### Week 1: Foundation

**Goal:** Get the basics working.

- Set up project structure: clients, models, tests, utils, config
- Built BaseClient with session management and basic logging
- Created Pydantic models for User, Resource, LoginRequest/Response
- Wrote first 20 tests (Users CRUD)
- Added pytest.ini, conftest.py with fixtures

**Problem I Hit:** Tests were flaky because of network hiccups (429s, occasional 5xx). 

**Fix:** Added retry logic to BaseClient using exponential backoff. Configurable retry count and backoff multiplier. Tests became resilient without slowing down.

### Week 2: Test Coverage

**Goal:** Get to 100+ tests.

- Added Resources API tests (28 tests)
- Authentication tests (login, register, token handling) (28 tests)
- E2E workflow tests (multi-step user journeys) (11 tests)
- Negative/edge case tests (invalid inputs, SQL injection, XSS) (23 tests)

**Problem I Hit:** Logs were leaking sensitive data (tokens, passwords).

**Fix:** Wrote a sanitizer in the logger that redacts known patterns (tokens, passwords, emails) before logging request/response bodies. Regex-based but simple.

### Week 3: CI/CD

**Goal:** Get everything running in GitHub Actions.

- Created `.github/workflows/api-tests.yml` (364 lines)
- 9 jobs: code quality, smoke tests, test matrix, parallel execution, coverage, Allure reports, regression, security, notifications
- Multi-stage Docker builds for faster CI runs
- Docker Compose profiles: full, smoke, users, resources, auth, parallel

**Problem I Hit:** CI runs were slow (15+ minutes).

**Fix:** Added parallel execution with pytest-xdist. Split tests across 5 jobs (users, resources, auth, workflows, negative). Full suite now runs in ~5 minutes.

### Week 4: Polish

**Goal:** Make it production-ready.

- Code coverage >80% (coverage.py)
- Type hints everywhere (mypy)
- Linting and formatting (black, isort, pylint)
- Allure reports auto-deployed to GitHub Pages
- HTML reports for local debugging
- Performance assertions (response time < 1s for critical endpoints)
- Schema validation with JSON Schema + Pydantic

---

## Decisions I Made (and Why)

### Python + Pytest + Requests

I could've used REST-assured (Java) or Postman/Newman, but I wanted full control. Python is readable, Pytest is powerful, Requests is simple. No magic, no abstractions I don't understand.

### Pydantic for Models

I needed type-safe validation without writing boilerplate. Pydantic gives me auto-validation, serialization, and readable error messages. If the API changes, my tests fail immediately with clear errors.

### Client Abstraction Layer

I didn't want every test to call `requests.get()` directly. The BaseClient handles retry, logging, session pooling, and response tracking. Specific clients (UsersClient, AuthClient) inherit from it and add endpoint-specific methods.

This means:
- Tests are readable (no HTTP noise)
- Retry logic is centralized
- Logs are consistent
- Easy to extend (new API? new client class)

### Retry with Exponential Backoff

External APIs are flaky. I used a retry library (tenacity) to handle 429 (rate limit) and 5xx (server errors) gracefully. Exponential backoff means we don't hammer the API when it's struggling.

### Parallel Execution

Sequential runs took 15+ minutes. pytest-xdist splits tests across workers. I went with 4 workers for balance (speed vs resource usage). CI runs 5 parallel jobs (one per suite).

### CI Pipeline Design

- Smoke tests run first (fast feedback, ~30s)
- If smoke passes, run the full suite in parallel
- Coverage check is last (don't block on it unless everything else passes)
- Daily regression runs catch API drift

---

## What Was Hard

### Flaky Tests

External APIs are unreliable. Rate limits, timeouts, occasional 5xx errors. I fixed this with:
- Retry logic (exponential backoff)
- Stateless tests (no cross-test dependencies)
- Unique test data per run (no collisions)

### Log Sanitization

I was logging full request/response bodies for debugging. That meant tokens, passwords, and emails in plain text. I wrote a sanitizer that redacts known patterns before logging.

### Parallel Execution

Tests were stepping on each other when run in parallel. I made every test stateless:
- Generate unique data per test (Faker)
- No shared fixtures with mutable state
- Isolate cross-test state behind fixtures with proper cleanup

### Schema Drift

APIs change. Fields get added, removed, renamed. I locked response validation behind Pydantic models. If the API changes, my tests fail immediately with clear errors.

---

## What I'd Do Differently

- **Contract Tests:** Pin schemas by API version. Right now I'm testing against the live API. I'd like to have versioned schemas and catch breaking changes earlier.
- **Chaos Engineering:** More negative scenarios (timeouts, malformed JSON, network partitions).
- **Stubbing Layer:** For local dev, I'd like to stub the network layer so tests run instantly.
- **Performance Profiling:** Wire K6 or Locust into CI for performance regression gates.

---

## Stats

- Total Tests: 125+
- Lines of Code: 3,500+
- Test Execution Time: ~5 minutes (parallel)
- Code Coverage: >80%
- CI Jobs: 9
- Docker Profiles: 6

---

## Tools I Used

- Python 3.11 (type hints, decorators)
- Pytest (fixtures, markers, parameterization)
- Requests (HTTP client)
- Pydantic (data validation)
- Black, isort, pylint, mypy (code quality)
- GitHub Actions (CI/CD)
- Docker + Docker Compose (containerization)
- Allure (reporting)
- Coverage.py (code coverage)
- Faker (test data generation)

---

## What I Learned

- Building a scalable test framework requires real architecture (not just piling tests into files)
- Retry logic is non-negotiable for external API tests
- Pydantic saves you from runtime validation hell
- Parallel execution is worth the setup cost
- Logs are useless if they leak secrets
- CI should fail fast (smoke first, full suite later)

---

Coffee consumed: Too much.

Times I rewrote the retry logic: 3.

Times I leaked a token in logs: 1 (fixed immediately).

Worth it? Absolutely.
