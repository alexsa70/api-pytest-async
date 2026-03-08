from __future__ import annotations

import allure
import pytest

from factories.organization_factory import OrganizationFactory
from services.organizations_service import OrganizationsService


@allure.epic("Organizations API")
@allure.feature("Smoke")
@pytest.mark.smoke
@pytest.mark.asyncio
async def test_create_organization_smoke(
    organizations_service: OrganizationsService,
    organization_factory: OrganizationFactory,
) -> None:
    payload = organization_factory.build_organization_create_request(exclusive_partner_only=True)

    created = await organizations_service.create_organization(payload)

    assert created.data.id >= 1
    assert created.data.name == payload.name
    assert created.data.exclusive_partner_only is True


@allure.epic("Organizations API")
@allure.feature("Smoke")
@pytest.mark.smoke
@pytest.mark.asyncio
async def test_create_organization_exclusive_partner_false_smoke(
    organizations_service: OrganizationsService,
    organization_factory: OrganizationFactory,
) -> None:
    payload = organization_factory.build_organization_create_request(exclusive_partner_only=False)

    created = await organizations_service.create_organization(payload)

    assert created.data.id >= 1
    assert created.data.name == payload.name
    assert created.data.exclusive_partner_only is False
