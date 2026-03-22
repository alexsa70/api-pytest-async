from __future__ import annotations

from collections.abc import AsyncIterator

import pytest_asyncio

from clients.api_client import APIClient
from config.settings import Settings
from services.devices.service import DevicesService
from tests.fixtures.auth import AuthSession


@pytest_asyncio.fixture
async def devices_service(api_client):
    return DevicesService(api_client)


@pytest_asyncio.fixture
async def integration_devices_service(
    settings: Settings,
    integration_auth_session: AuthSession,
) -> AsyncIterator[DevicesService]:
    client = APIClient(
        base_url=settings.api_base_url,
        timeout=settings.api_timeout,
        retries=settings.api_retries,
        retry_backoff=settings.api_retry_backoff,
        auth_token_getter=integration_auth_session.get_token,
        auth_token_refresher=integration_auth_session.refresh_token,
    )
    try:
        yield DevicesService(client)
    finally:
        await client.close()
