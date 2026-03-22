from __future__ import annotations

from collections.abc import AsyncIterator

import httpx
import pytest_asyncio

from clients.api_client import APIClient
from config.settings import Settings
from tests.fixtures.auth import AuthSession

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
