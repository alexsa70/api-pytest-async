# API Test Framework

Async, layered API testing framework using `pytest`, `httpx`, `pydantic`, JSON Schema validation, OpenAPI contract checks, Schemathesis fuzzing, Allure reporting, parallelization, and CI quality gates.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Run tests

Activate the virtual environment first:

```bash
source .venv/bin/activate
```

Run all default tests (smoke + contract) in parallel:

```bash
pytest -m "smoke or contract" -n auto
```

Run by individual marker:

```bash
pytest -m smoke -n auto       # happy-path critical paths
pytest -m contract -n auto    # schema/contract + negative cases
```

Run optional suites (disabled by default):

```bash
RUN_INTEGRATION=true pytest -m integration   # real API calls
RUN_FUZZ=true pytest -m fuzz                 # Schemathesis OpenAPI fuzzing
```

Run a single file or test:

```bash
pytest tests/smoke/test_organizations_smoke.py
pytest tests/integration/test_organizations_integration.py::test_real_api_organization_e2e_create_verify_modify_verify
```

## Users Layer Status

`users` models/services/factories are intentionally kept as a reusable reference template for future endpoints/projects.

- They are not part of the active `stage2` coverage right now.
- Active real coverage is focused on `organizations` (v2 create/get/patch + v1 delete cleanup in integration).

## Coverage gate

```bash
pytest -m "smoke or contract" -n auto \
  --cov=clients --cov=services --cov=models --cov=utils \
  --cov-report=term-missing --cov-fail-under=85
```

## Allure report

Generate results and open the report in a browser:

```bash
# 1. Run tests and collect results
pytest -m "smoke or contract" -n auto --alluredir=allure-results

# 2. Serve the interactive report (opens browser automatically)
allure serve allure-results
```

To generate a static HTML report instead:

```bash
allure generate allure-results -o allure-report --clean
open allure-report/index.html   # macOS
```

> **Prerequisite:** install Allure CLI — `brew install allure` (macOS) or see https://docs.qameta.io/allure/#_installing_a_commandline

## Pre-commit

```bash
pre-commit install
pre-commit run --all-files
```
