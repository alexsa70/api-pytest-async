from __future__ import annotations

import json
from collections.abc import AsyncIterator

import httpx
import pytest
import pytest_asyncio

from clients.api_client import APIClient
from config.settings import Settings
from models.user_models import User
from services.organizations_service import OrganizationsService
from services.organizations_v1_service import OrganizationsV1Service
from services.organizations_v2_service import OrganizationsV2Service
from services.users_service import UsersService
from tests.fixtures.auth import AuthSession
from utils.endpoints import AUTH_LOGIN, ORGANIZATIONS, USERS


@pytest.fixture
def mock_organizations_store() -> dict[int, dict[str, object]]:
    return {}


@pytest.fixture
def mock_transport(
    mock_users_store: dict[int, User],
    mock_organizations_store: dict[int, dict[str, object]],
    settings: Settings,
) -> httpx.MockTransport:
    tokens_issued = {"count": 0}

    def _is_authorized(request: httpx.Request) -> bool:
        auth = request.headers.get("Authorization", "")
        return auth.startswith("Bearer mock-token-")

    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == AUTH_LOGIN and request.method == "POST":
            body = json.loads(request.content.decode("utf-8"))
            username_or_email = body.get("email", body.get("username"))
            if username_or_email != settings.auth_username or body.get("password") != settings.auth_password:
                return httpx.Response(status_code=401, json={"detail": "Invalid credentials"})

            tokens_issued["count"] += 1
            return httpx.Response(
                status_code=200,
                json={
                    "access_token": f"mock-token-{tokens_issued['count']}",
                    "token_type": "Bearer",
                    "expires_in": 1,
                },
            )

        if not _is_authorized(request):
            return httpx.Response(status_code=401, json={"detail": "Unauthorized"})

        if request.url.path == USERS and request.method == "GET":
            if request.url.params.get("trigger") == "500":
                return httpx.Response(status_code=500, json={"detail": "Internal error"})
            payload = {
                "data": [user.model_dump() for user in mock_users_store.values()],
                "total": len(mock_users_store),
            }
            return httpx.Response(status_code=200, json=payload)

        if request.url.path == USERS and request.method == "POST":
            if request.headers.get("X-Role") == "guest":
                return httpx.Response(status_code=403, json={"detail": "Forbidden"})

            if request.content == b"":
                return httpx.Response(status_code=400, json={"detail": "Bad request"})

            body = json.loads(request.content.decode("utf-8"))
            required = {"email", "first_name", "last_name"}
            if not required.issubset(body.keys()):
                return httpx.Response(status_code=422, json={"detail": "Validation error"})

            if body.get("first_name") == "Trigger500":
                return httpx.Response(status_code=500, json={"detail": "Internal error"})

            new_id = max(mock_users_store.keys()) + 1 if mock_users_store else 1
            new_user = User(id=new_id, is_active=True, **body)
            mock_users_store[new_id] = new_user
            return httpx.Response(status_code=201, json={"data": new_user.model_dump()})

        if request.url.path.startswith("/users/") and request.method == "GET":
            user_id_segment = request.url.path.split("/")[-1]
            if user_id_segment == "forbidden":
                return httpx.Response(status_code=403, json={"detail": "Forbidden"})

            if user_id_segment == "500":
                return httpx.Response(status_code=500, json={"detail": "Internal error"})

            try:
                user_id = int(user_id_segment)
            except ValueError:
                return httpx.Response(status_code=400, json={"detail": "Invalid user id"})

            user = mock_users_store.get(user_id)
            if user is None:
                return httpx.Response(status_code=404, json={"detail": "Not found"})
            return httpx.Response(status_code=200, json={"data": user.model_dump()})

        if request.url.path == ORGANIZATIONS and request.method == "POST":
            if request.content == b"":
                return httpx.Response(status_code=400, json={"detail": "Bad request"})

            body = json.loads(request.content.decode("utf-8"))

            if not body.get("name"):
                return httpx.Response(status_code=422, json={"detail": "Validation error"})

            if request.headers.get("X-Role") == "guest":
                return httpx.Response(status_code=403, json={"detail": "Forbidden"})

            if body.get("name") == "Trigger500":
                return httpx.Response(status_code=500, json={"detail": "Internal error"})

            new_id = max(mock_organizations_store.keys()) + 1 if mock_organizations_store else 1
            new_org: dict[str, object] = {
                "id": new_id,
                "name": body["name"],
                "exclusivePartnerOnly": body.get("exclusivePartnerOnly", False),
            }
            mock_organizations_store[new_id] = new_org
            return httpx.Response(status_code=201, json={"data": new_org})

        return httpx.Response(status_code=404, json={"detail": "Route not found"})

    return httpx.MockTransport(handler)


_MOCK_BASE_URL = "http://test"


@pytest_asyncio.fixture
async def api_client(
    settings: Settings,
    mock_transport: httpx.MockTransport,
    auth_session: AuthSession,
) -> AsyncIterator[APIClient]:
    client = APIClient(
        base_url=_MOCK_BASE_URL,
        timeout=settings.api_timeout,
        headers={"Content-Type": "application/json"},
        transport=mock_transport,
        auth_token_getter=auth_session.get_token,
        auth_token_refresher=auth_session.refresh_token,
        retries=settings.api_retries,
        retry_backoff=settings.api_retry_backoff,
    )
    try:
        yield client
    finally:
        await client.close()


@pytest_asyncio.fixture
async def users_service(api_client: APIClient) -> UsersService:
    return UsersService(api_client)


@pytest_asyncio.fixture
async def integration_client(settings: Settings) -> AsyncIterator[APIClient]:
    client = APIClient(
        base_url=settings.api_base_url,
        timeout=settings.api_timeout,
        retries=settings.api_retries,
        retry_backoff=settings.api_retry_backoff,
    )
    try:
        yield client
    finally:
        await client.close()


@pytest_asyncio.fixture
async def integration_users_service(integration_client: APIClient) -> UsersService:
    return UsersService(integration_client)


@pytest_asyncio.fixture
async def organizations_service(api_client: APIClient) -> OrganizationsService:
    return OrganizationsService(api_client)


@pytest_asyncio.fixture
async def integration_organizations_service(
    settings: Settings,
    integration_auth_session: AuthSession,
) -> AsyncIterator[OrganizationsService]:
    client = APIClient(
        base_url=settings.api_base_url,
        timeout=settings.api_timeout,
        retries=settings.api_retries,
        retry_backoff=settings.api_retry_backoff,
        auth_token_getter=integration_auth_session.get_token,
        auth_token_refresher=integration_auth_session.refresh_token,
    )
    try:
        yield OrganizationsService(client)
    finally:
        await client.close()


@pytest_asyncio.fixture
async def integration_organizations_v2_service(
    settings: Settings,
    integration_auth_session: AuthSession,
) -> AsyncIterator[OrganizationsV2Service]:
    client = APIClient(
        base_url=settings.api_base_url,
        timeout=settings.api_timeout,
        retries=settings.api_retries,
        retry_backoff=settings.api_retry_backoff,
        auth_token_getter=integration_auth_session.get_token,
        auth_token_refresher=integration_auth_session.refresh_token,
    )
    try:
        yield OrganizationsV2Service(client)
    finally:
        await client.close()


@pytest_asyncio.fixture
async def integration_organizations_v1_service(settings: Settings) -> AsyncIterator[OrganizationsV1Service]:
    client = APIClient(
        base_url=settings.api_v1_base_url,
        timeout=settings.api_timeout,
        retries=settings.api_retries,
        retry_backoff=settings.api_retry_backoff,
    )
    try:
        yield OrganizationsV1Service(client)
    finally:
        await client.close()
