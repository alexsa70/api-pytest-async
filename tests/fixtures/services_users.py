from __future__ import annotations

import pytest_asyncio

from services.users.service import UsersService


# Reference template fixtures for future user endpoints.
@pytest_asyncio.fixture
async def users_service(api_client):
    return UsersService(api_client)


@pytest_asyncio.fixture
async def integration_users_service(integration_client):
    return UsersService(integration_client)
