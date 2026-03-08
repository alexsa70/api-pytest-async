# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Commands

```bash
# Run tests by marker (parallel)
pytest -m smoke -n auto
pytest -m contract -n auto
pytest -m "smoke or contract" -n auto

# Optional test suites (disabled by default)
RUN_INTEGRATION=true pytest -m integration
RUN_FUZZ=true pytest -m fuzz

# Run a single test file or test
pytest tests/smoke/test_users_smoke.py
pytest tests/smoke/test_users_smoke.py::test_get_user

# Coverage gate (85% minimum)
pytest -m "smoke or contract" -n auto \
  --cov=clients --cov=services --cov=models --cov=utils \
  --cov-report=term-missing --cov-fail-under=85

# Allure reporting
pytest --alluredir=allure-results && allure serve allure-results

# Linting / formatting
pre-commit run --all-files
```

## Architecture

The framework uses a strict layered architecture. Always follow this separation:

```
clients/        → HTTP layer (httpx.AsyncClient wrapper with retries, auth)
services/       → Business logic (wraps client, handles Pydantic serialization)
models/         → Pydantic v2 request/response models
factories/      → Test data generation (Faker-based)
utils/          → Shared helpers: validators, assertions, endpoints, schema_diff
config/         → Settings (pydantic-settings, loaded from .env)
schemas/        → JSON Schema definitions for contract validation
openapi/        → OpenAPI spec (used by Schemathesis fuzz tests)
tests/          → Test suite organized by type (smoke/contract/integration/fuzz)
```

**Key constraint:** Service classes must not contain HTTP logic; `ApiClient` must not contain business logic.

### clients/api_client.py

Central `ApiClient` class handles:

- Bearer token auth with automatic 401 → token refresh callback
- Retry with exponential backoff for 429 and 5xx responses
- `expected_status` parameter for inline status assertion
- All methods are async (`get`, `post`, `put`, `patch`, `delete`)

### tests/fixtures/

Fixtures are split into three modules loaded via `pytest_plugins` in `tests/conftest.py`:

- `tests/fixtures/data.py` — settings, faker, factories, JSON schemas
- `tests/fixtures/auth.py` — `AuthSession` with auto token refresh
- `tests/fixtures/api.py` — mock transport, `ApiClient`, services

The mock transport in `api.py` simulates the full API (auth, user CRUD, error injection) and is used by all non-integration tests.

### Validation strategy

Every response goes through two validation layers via `utils/validators.py`:

1. **Pydantic** — type + constraint validation
2. **JSON Schema (Draft 7)** — structural/contract validation

Use `validate_response(data, model=..., schema=...)` rather than validating separately.

### Test markers

| Marker | Purpose | Default |
|--------|---------|---------|
| `smoke` | Happy-path critical paths | Always run |
| `contract` | Schema/contract + negative cases | Always run |
| `integration` | Real API calls | `RUN_INTEGRATION=true` |
| `fuzz` | Schemathesis OpenAPI fuzzing | `RUN_FUZZ=true` |
| `negative` | Error/rejection scenarios | Always run |

## Configuration

Settings are loaded from `.env` via `config/settings.py` (pydantic-settings). Key variables:

```

API_BASE_URL, API_TIMEOUT, API_RETRIES, API_RETRY_BACKOFF
AUTH_USERNAME, AUTH_PASSWORD
OPENAPI_PATH
RUN_INTEGRATION, RUN_FUZZ
ENV
```

## Code style

- Line length: 100 (Black + Ruff)
- Python 3.11+, async/await throughout
- Pydantic v2 models use `ConfigDict(extra="forbid")`
- Mypy strict mode is enforced via pre-commit

### Agents roles

**python-expert**: Для код-ревью, планирования фич и соблюдения стиля.
**python-debugger**: Только для исправления ошибок и анализа падений.
**test-gen-expert**: Предлагает вариант теста в соотвествии со структурой проекта если введен cURL как PROMPT.
