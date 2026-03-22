from __future__ import annotations

from collections.abc import AsyncIterator

import pytest_asyncio

from clients.api_client import APIClient
from config.settings import Settings
from services.organizations.service import OrganizationsService
from services.organizations.v1_service import OrganizationsV1Service
from services.organizations.v2_service import OrganizationsV2Service
from tests.fixtures.auth import AuthSession


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
