# Python Debugger Agent Memory

## Project: api-test-async

### Key Architectural Notes

- Mock-based tests (`smoke`, `contract`) use `httpx.MockTransport` and do NOT hit the real API.
- The real API base URL in `.env` is `https://api.stage2.surfsight.net/v2` (includes `/v2` path segment).
- Mock transport fixtures must use a base URL WITHOUT a path prefix (`http://test`), otherwise httpx prepends the path and the mock handler path comparisons fail.

---

## Bug: Mock Transport Auth 401 — base_url Path Prefix

**File affected**: `tests/fixtures/auth.py`, `tests/fixtures/api.py`

**Symptom**: All tests fail with `httpx.HTTPStatusError: Expected status 200, got 401` during `auth_session` fixture setup.

**Root cause**: `auth_client` and `api_client` were using `settings.api_base_url` (`https://api.stage2.surfsight.net/v2`) as the base URL. When httpx resolves a request to `/auth/login` against this base URL, the actual path seen by the mock handler is `/v2/auth/login`. The mock handler checks `request.url.path == "/auth/login"`, which fails. The request then hits the `_is_authorized()` guard (no Bearer token for login call) and returns 401.

**Fix**: Use `_MOCK_BASE_URL = "http://test"` (no path component) as the base URL for mock-based `APIClient` fixtures.

```python
# tests/fixtures/auth.py
_MOCK_BASE_URL = "http://test"

@pytest_asyncio.fixture
async def auth_client(...) -> AsyncIterator[APIClient]:
    client = APIClient(base_url=_MOCK_BASE_URL, ...)

# tests/fixtures/api.py
_MOCK_BASE_URL = "http://test"

@pytest_asyncio.fixture
async def api_client(...) -> AsyncIterator[APIClient]:
    client = APIClient(base_url=_MOCK_BASE_URL, ...)
```

**Prevention**: When adding new mock-based API client fixtures, ALWAYS use `_MOCK_BASE_URL = "http://test"`, never `settings.api_base_url`. Integration fixtures (those hitting the real API) should use `settings.api_base_url`.

**Verification**: `pytest -m "smoke or contract" -n auto -v` — 24 passed.

---

## Recurring Gotcha: Token Expiry with expires_in=1

The mock transport returns `expires_in: 1` for auth tokens. `AuthSession.get_token()` checks `monotonic() >= expires_at - 1`, which equates to `monotonic() >= time_of_last_refresh`. This means the token is "expired" on the very next call. This is intentional — it exercises the auto-refresh path — but it means `refresh_token()` is called on every `get_token()` invocation in tests. This is fine as long as the mock base URL is correct (see bug above).
