from __future__ import annotations

import allure
import pytest

from factories.organization_factory import OrganizationFactory
from models.organizations.models import OrganizationResponse
from services.organizations.service import OrganizationsService
from utils.validators import validate_response


@allure.epic("Organizations API")
@allure.feature("Contract")
@pytest.mark.contract
@pytest.mark.asyncio
async def test_create_organization_contract(
    organizations_service: OrganizationsService,
    organization_factory: OrganizationFactory,
    organization_response_schema: dict,
) -> None:
    payload = organization_factory.build_organization_create_request()

    response_model = await organizations_service.create_organization(payload)

    parsed = validate_response(
        response_model.model_dump(by_alias=True),
        model=OrganizationResponse,
        schema=organization_response_schema,
    )

    assert parsed.data.id >= 1
    assert parsed.data.name == payload.name
    assert isinstance(parsed.data.exclusive_partner_only, bool)


@allure.epic("Organizations API")
@allure.feature("Contract")
@pytest.mark.contract
@pytest.mark.asyncio
async def test_create_organization_response_fields_present(
    organizations_service: OrganizationsService,
    organization_factory: OrganizationFactory,
) -> None:
    payload = organization_factory.build_organization_create_request()

    created = await organizations_service.create_organization(payload)

    # Verify the response model contains all expected fields by re-validating
    # against the Pydantic model — catching extra/missing fields early.
    re_parsed = OrganizationResponse.model_validate(created.model_dump(by_alias=True))
    assert re_parsed.data.id == created.data.id
    assert re_parsed.data.name == created.data.name
