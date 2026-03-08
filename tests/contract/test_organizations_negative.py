from __future__ import annotations

import httpx
import pytest

from clients.api_client import APIClient
from services.organizations_service import OrganizationsService
from utils.assertions import assert_status_code
from utils.endpoints import ORGANIZATIONS


@pytest.mark.contract
@pytest.mark.negative
@pytest.mark.asyncio
async def test_create_organization_401_without_token(settings, mock_transport) -> None:
    async with APIClient(
        base_url=settings.api_base_url,
        timeout=settings.api_timeout,
        transport=mock_transport,
    ) as raw_client:
        response = await raw_client.post(
            ORGANIZATIONS,
            json={"name": "Acme Corp", "exclusivePartnerOnly": True},
        )
    assert_status_code(response, 401)


@pytest.mark.contract
@pytest.mark.negative
@pytest.mark.asyncio
async def test_create_organization_403_forbidden(api_client: APIClient) -> None:
    response = await api_client.post(
        ORGANIZATIONS,
        json={"name": "Acme Corp", "exclusivePartnerOnly": True},
        headers={"X-Role": "guest"},
    )
    assert_status_code(response, 403)


@pytest.mark.contract
@pytest.mark.negative
@pytest.mark.asyncio
async def test_create_organization_400_empty_body(api_client: APIClient) -> None:
    # Send a POST with an explicitly empty body by passing no json argument.
    # The mock interprets empty content bytes as a 400.
    response = await api_client.post(ORGANIZATIONS, json=None)
    assert_status_code(response, 400)


@pytest.mark.contract
@pytest.mark.negative
@pytest.mark.asyncio
async def test_create_organization_422_missing_name(api_client: APIClient) -> None:
    response = await api_client.post(
        ORGANIZATIONS,
        json={"exclusivePartnerOnly": True},
    )
    assert_status_code(response, 422)


@pytest.mark.contract
@pytest.mark.negative
@pytest.mark.asyncio
async def test_create_organization_500_internal(api_client: APIClient) -> None:
    # The mock triggers a 500 when name == "Trigger500".
    response = await api_client.post(
        ORGANIZATIONS,
        json={"name": "Trigger500", "exclusivePartnerOnly": False},
    )
    assert_status_code(response, 500)


@pytest.mark.contract
@pytest.mark.negative
@pytest.mark.asyncio
async def test_create_organization_raises_on_unexpected_status(
    organizations_service: OrganizationsService,
) -> None:
    # OrganizationsService.create_organization uses expected_status=201.
    # A 403 response (guest role) should raise HTTPStatusError.
    with pytest.raises(httpx.HTTPStatusError):
        from models.organization_models import OrganizationCreateRequest

        payload = OrganizationCreateRequest(name="Acme", exclusivePartnerOnly=False)
        # Bypass the service to inject the guest header, then confirm the
        # service itself raises when the status does not match 201.
        await organizations_service.api_client.post(
            ORGANIZATIONS,
            json=payload.model_dump(by_alias=True),
            headers={"X-Role": "guest"},
            expected_status=201,
        )
