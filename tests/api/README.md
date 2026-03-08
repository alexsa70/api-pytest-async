# API Tests Organization

Tests are split by intent:
- `tests/smoke/` for critical happy paths
- `tests/contract/` for schema/contract coverage and negative scenarios
- `tests/integration/` for real environment checks
- `tests/fuzz/` for Schemathesis fuzz testing
