# API Test Automation Framework

[![CI/CD](https://github.com/JasonTeixeira/API-Test-Automation-Wireframe/actions/workflows/api-tests.yml/badge.svg)](https://github.com/JasonTeixeira/API-Test-Automation-Wireframe/actions/workflows/api-tests.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Enterprise-grade REST API test automation framework built with Python, Pytest, and Requests. Features **125+ comprehensive tests**, CI/CD integration, Docker support, and professional reporting.

## 🎯 Key Features

- **125+ Comprehensive Tests** - Full coverage of CRUD operations, authentication, workflows, and edge cases
- **Enterprise Architecture** - Client abstraction layer with retry logic, logging, and response tracking
- **Type-Safe Models** - Pydantic models for request/response validation with custom validators
- **Schema Validation** - JSON Schema + Pydantic validation for API contract testing
- **CI/CD Pipeline** - Multi-stage GitHub Actions workflow with parallel execution
- **Docker Support** - Containerized execution with docker-compose orchestration
- **Rich Reporting** - Allure reports, HTML reports, and code coverage tracking
- **Performance Testing** - Response time assertions and performance thresholds
- **Security Testing** - SQL injection, XSS, and security vulnerability tests
- **Professional Logging** - Colored console output with request/response sanitization

## 📊 Test Coverage

| Test Suite | Tests | Coverage |
|------------|-------|----------|
| **Users API** | 35 | CRUD, pagination, schema validation, performance |
| **Resources API** | 28 | CRUD, data integrity, error handling |
| **Authentication** | 28 | Login, register, token management, security |
| **Workflows** | 11 | E2E user journeys, multi-step operations |
| **Negative/Edge Cases** | 23 | Invalid inputs, boundary values, security |
| **Total** | **125+** | **Full API coverage** |

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- pip package manager
- (Optional) Docker and Docker Compose

### Installation

```bash
# Clone the repository
git clone https://github.com/JasonTeixeira/API-Test-Automation-Wireframe.git
cd API-Test-Automation-Wireframe

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run smoke tests (fast feedback)
pytest tests/ -m smoke -v

# Run specific test suite
pytest tests/users/ -v

# Run with coverage
pytest tests/ --cov=clients --cov=models --cov=utils --cov=config

# Run in parallel
pytest tests/ -n 4 -v

# Generate HTML report
pytest tests/ --html=reports/report.html --self-contained-html

# Generate Allure report
pytest tests/ --alluredir=reports/allure-results
allure serve reports/allure-results
```

### Docker Execution

```bash
# Run all tests
docker-compose --profile full up test-runner

# Run smoke tests
docker-compose --profile smoke up smoke-tests

# Run specific test suite
docker-compose --profile users up users-tests

# Run in parallel
docker-compose --profile parallel up parallel-tests
```

## 📁 Project Structure

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

## 🏗️ Architecture

### Client Layer

```python
from clients.users_client import UsersClient

client = UsersClient()
response = client.get_users(page=1, per_page=10)

assert response.is_success()
assert response.status_code == 200
assert response.elapsed_time < 1.0
```

**Features:**
- Automatic retry with exponential backoff
- Request/response logging with sanitization
- Session management
- Response time tracking
- Error handling

### Model Layer

```python
from models.schemas import User, validate_user_schema

# Pydantic validation
user = User(**response_data)

# JSON Schema validation
validated = validate_user_schema(response_data)
```

**Features:**
- Type-safe Pydantic models
- Custom validators
- JSON Schema validation
- Request/response models

### Test Layer

```python
@pytest.mark.users
@pytest.mark.smoke
def test_get_user(users_client, existing_user_id):
    """Test retrieving an existing user."""
    response = users_client.get_user(existing_user_id)
    
    assert response.is_success()
    assert response.json["data"]["id"] == existing_user_id
```

## 🧪 Test Markers

Run specific test categories:

```bash
pytest -m smoke        # Critical path tests
pytest -m regression   # Full regression suite
pytest -m users        # User API tests
pytest -m resources    # Resource API tests
pytest -m auth         # Authentication tests
pytest -m workflows    # E2E workflow tests
pytest -m security     # Security tests
pytest -m performance  # Performance tests
pytest -m negative     # Negative/edge cases
```

## 📈 CI/CD Pipeline

The GitHub Actions workflow includes 9 jobs:

1. **Code Quality** - Black, isort, pylint, mypy
2. **Smoke Tests** - Fast feedback on critical paths
3. **API Test Matrix** - 5 parallel jobs (users, resources, auth, workflows, negative)
4. **Parallel Tests** - Full suite with 4 workers
5. **Coverage Analysis** - Code coverage with >80% target
6. **Allure Reports** - Rich reporting deployed to GitHub Pages
7. **Regression Suite** - Daily scheduled runs
8. **Security Tests** - Dedicated security testing
9. **Notifications** - Test result summaries

## 🐳 Docker Support

### Quick Commands

```bash
# Full test suite
docker-compose --profile full up test-runner

# Smoke tests
docker-compose --profile smoke up smoke-tests

# Parallel execution
docker-compose --profile parallel up parallel-tests
```

### Multi-Stage Dockerfile

- **Base**: Python 3.11 slim
- **Dependencies**: Cached pip installs
- **Test Runner**: Complete environment
- **Specialized**: Suite-specific images

## 📊 Reporting

### HTML Reports

Self-contained HTML reports in `reports/html/`:
- Test results with pass/fail status
- Execution times
- Error traces and screenshots

### Allure Reports

```bash
pytest tests/ --alluredir=reports/allure-results
allure serve reports/allure-results
```

Features:
- Test execution timeline
- Historical trends
- Failure analysis
- Request/response details
- Test categories

### Code Coverage

```bash
pytest tests/ --cov=clients --cov=models --cov=utils --cov=config \
  --cov-report=html --cov-report=term

open htmlcov/index.html
```

Target: >80% coverage for production code

## ⚙️ Configuration

### Environment Variables

Configure via `.env` file:

```bash
API_BASE_URL=https://reqres.in/api
API_TIMEOUT=30
API_RETRY_COUNT=3
PARALLEL_WORKERS=4
LOG_LEVEL=INFO
PERFORMANCE_THRESHOLD_MS=1000
```

### Pydantic Settings

Type-safe configuration in `config/settings.py`:

```python
from config.settings import settings

settings.api_base_url      # https://reqres.in/api
settings.api_timeout       # 30
settings.parallel_workers  # 4
```

## 🔧 Development

### Code Quality Tools

```bash
# Format code
black .
isort .

# Lint
pylint clients/ models/ utils/ config/

# Type check
mypy clients/ models/ utils/ config/
```

### Adding New Tests

1. Create test file in appropriate directory
2. Use fixtures from `conftest.py`
3. Add pytest markers
4. Follow AAA pattern
5. Include docstrings

## 🎓 What This Framework Demonstrates

### Technical Skills

- **Python Expertise** - Type hints, decorators, context managers
- **API Testing** - REST APIs, HTTP methods, status codes
- **Test Automation** - Pytest, fixtures, markers, parameterization
- **CI/CD** - GitHub Actions, multi-stage pipelines
- **Docker** - Multi-stage builds, docker-compose
- **Architecture** - Clean code, SOLID principles, DRY
- **Documentation** - Comprehensive README, docstrings

### Professional Practices

- **125+ Production-Grade Tests** - Complete API coverage
- **Enterprise Architecture** - Scalable, maintainable design
- **CI/CD Integration** - Automated testing pipeline
- **Code Quality** - Linting, formatting, type checking
- **Security Testing** - SQL injection, XSS, vulnerability scanning
- **Performance Testing** - Response time assertions
- **Professional Logging** - Structured, sanitized logging
- **Rich Reporting** - Allure, HTML, coverage reports

### Portfolio Highlights

✅ **Complex System**: 3,500+ lines of production code  
✅ **Best Practices**: PEP 8, type hints, docstrings  
✅ **DevOps Integration**: Complete CI/CD pipeline  
✅ **Docker**: Production-ready containerization  
✅ **Documentation**: Comprehensive technical docs  
✅ **Test Coverage**: 125+ tests with >80% code coverage  

## 📚 Additional Documentation

- [TEST_ARCHITECTURE.md](docs/TEST_ARCHITECTURE.md) - Test patterns and organization
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Portfolio summary

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

## 📝 License

MIT License - see [LICENSE](LICENSE) file.

## 📞 Contact

**Jason Teixeira**  
GitHub: [@JasonTeixeira](https://github.com/JasonTeixeira)  
Project: [API-Test-Automation-Wireframe](https://github.com/JasonTeixeira/API-Test-Automation-Wireframe)

---

**⭐ Star this repo if you find it useful for learning API test automation!**

**Built with ❤️ for professional QA automation engineering**
