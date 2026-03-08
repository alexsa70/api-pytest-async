# test-gen-expert Memory

## Project: api-test-async

### Python runtime
- Project requires Python 3.11+. Use `/Users/alex.lechtchinski/.pyenv/versions/3.11.13/bin/python3.11` to run pytest.
- No .venv in the project root — install deps directly into pyenv 3.11 if needed.
- Run tests: `/Users/alex.lechtchinski/.pyenv/versions/3.11.13/bin/python3.11 -m pytest ...`

### Architecture (strict layered pattern)
- `APIClient` (clients/api_client.py) — raw HTTP, auth, retries. No business logic.
- `XService` (services/) — wraps APIClient, calls `model_validate`, returns Pydantic models.
- `models/` — Pydantic v2 models. Use `ConfigDict(extra="forbid")` on response item models.
- `factories/` — Faker-based test-data builders.
- `schemas/` — JSON Schema Draft 7 files for `validate_response()`.
- `tests/fixtures/api.py` — mock_transport + service fixtures.
- `tests/fixtures/data.py` — settings, faker, factory, schema fixtures.
- `tests/fixtures/auth.py` — AuthSession fixture.

### Key conventions
- All service methods call `api_client.post/get(..., expected_status=NNN)`.
- Service POST uses `payload.model_dump(by_alias=True)` to serialise aliased fields.
- `validate_response(model.model_dump(by_alias=True), model=XResponse, schema=schema)` in contract tests.
- Tests use `@pytest.mark.asyncio` even though `asyncio_mode = auto` is set (existing codebase convention).
- Markers: `smoke`, `contract`, `negative` (negative tests combine `contract` + `negative`).
- All new files start with `from __future__ import annotations`.
- Line length 100, Black + Ruff.

### Adding a new domain (e.g. organizations)
1. `models/X_models.py` — XCreateRequest, X (item with `extra="forbid"`), XResponse.
2. `utils/endpoints.py` — add `X = "/x"` constant.
3. `services/X_service.py` — XService(api_client), method returns XResponse.
4. `factories/X_factory.py` — XFactory(faker), `build_X_create_request()` + dict variant.
5. `schemas/X_schema.json` — Draft-7, mirrors XResponse structure.
6. `tests/fixtures/api.py` — add `mock_X_store` fixture, extend `mock_transport` handler, add `X_service` fixture.
7. `tests/fixtures/data.py` — add `X_factory` and `X_response_schema` fixtures.
8. `tests/smoke/test_X_smoke.py` — happy path.
9. `tests/contract/test_X_contract.py` — schema + pydantic double validation.
10. `tests/contract/test_X_negative.py` — 400/401/403/422/500 cases.

### Pydantic alias pattern
- Use `Field(alias="camelCase")` + `ConfigDict(populate_by_name=True)` when the API uses camelCase JSON.
- Serialise with `model_dump(by_alias=True)` in service methods and contract test assertions.
- Mock transport stores and returns data using the camelCase alias keys (raw dict), not Python attribute names.

### Details link
See `patterns.md` for extended notes.
