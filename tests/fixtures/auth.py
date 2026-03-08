from __future__ import annotations

import time
from collections.abc import AsyncIterator

import httpx
import pytest_asyncio

from clients.api_client import APIClient
from config.settings import Settings
from models.auth_models import AuthLoginRequest
from services.auth_service import AuthService


class AuthSession:
    def __init__(self, auth_service: AuthService, settings: Settings) -> None:
        self._auth_service = auth_service
        self._settings = settings
        self._token: str | None = None
        self._expires_at: float = 0.0

    async def refresh_token(self) -> str:
        token_response = await self._auth_service.login(
            AuthLoginRequest(
                email=self._settings.auth_username,
                password=self._settings.auth_password,
            )
        )
        self._token = token_response.token
        self._expires_at = time.monotonic() + token_response.ttl_seconds
        return self._token

    async def get_token(self) -> str:
        if self._token is None or time.monotonic() >= (self._expires_at - 1):
            await self.refresh_token()
        return self._token


_MOCK_BASE_URL = "http://test"


@pytest_asyncio.fixture
async def auth_client(settings: Settings, mock_transport: httpx.MockTransport) -> AsyncIterator[APIClient]:
    client = APIClient(
        base_url=_MOCK_BASE_URL,
        timeout=settings.api_timeout,
        headers={"Content-Type": "application/json"},
        transport=mock_transport,
        retries=settings.api_retries,
        retry_backoff=settings.api_retry_backoff,
    )
    try:
        yield client
    finally:
        await client.close()


@pytest_asyncio.fixture
async def auth_service(auth_client: APIClient) -> AuthService:
    return AuthService(auth_client)


@pytest_asyncio.fixture
async def auth_session(auth_service: AuthService, settings: Settings) -> AuthSession:
    session = AuthSession(auth_service=auth_service, settings=settings)
    await session.refresh_token()
    return session


@pytest_asyncio.fixture
async def integration_auth_session(settings: Settings) -> AsyncIterator[AuthSession]:
    client = APIClient(
        base_url=settings.api_base_url,
        timeout=settings.api_timeout,
        headers={"Content-Type": "application/json"},
        retries=settings.api_retries,
        retry_backoff=settings.api_retry_backoff,
    )
    try:
        auth_service = AuthService(client)
        session = AuthSession(auth_service=auth_service, settings=settings)
        await session.refresh_token()
        yield session
    finally:
        await client.close()
