from __future__ import annotations

from uuid import uuid4

import pytest

from config.settings import Settings
from factories.organization_factory import OrganizationFactory
from models.organizations.v2_models import OrganizationV2PatchRequest
from services.organizations.v1_service import OrganizationsV1Service
from services.organizations.v2_service import OrganizationsV2Service
from tests.fixtures.auth import AuthSession


@pytest.mark.integration
@pytest.mark.skipif(not Settings().run_integration, reason="Set RUN_INTEGRATION=true for real API tests")
@pytest.mark.asyncio
async def test_real_api_organization_e2e_create_verify_modify_verify(
    integration_organizations_v2_service: OrganizationsV2Service,
    integration_organizations_v1_service: OrganizationsV1Service,
    integration_auth_session: AuthSession,
    organization_factory: OrganizationFactory,
) -> None:
    payload = organization_factory.build_organization_create_request(exclusive_partner_only=True)
    unique_suffix = uuid4().hex[:8]
    payload.name = f"{payload.name}-{unique_suffix}"
    updated_name = f"{payload.name}-updated"
    organization_id: int | None = None

    try:
        created = await integration_organizations_v2_service.create_organization(payload)
        assert created.organization_id >= 1
        organization_id = created.organization_id

        created_org = await integration_organizations_v2_service.get_organization(created.organization_id)
        assert created_org.data.id == created.organization_id
        assert created_org.data.name == payload.name
        assert created_org.data.exclusive_partner_only is True

        patch_response = await integration_organizations_v2_service.patch_organization(
            created.organization_id,
            OrganizationV2PatchRequest(name=updated_name, exclusive_partner_only=False),
        )
        assert patch_response.request_id

        updated_org = await integration_organizations_v2_service.get_organization(created.organization_id)
        assert updated_org.data.id == created.organization_id
        assert updated_org.data.name == updated_name
        assert updated_org.data.exclusive_partner_only is False
    finally:
        if organization_id is not None:
            token = await integration_auth_session.get_token()
            await integration_organizations_v1_service.delete_organization(organization_id, token)
