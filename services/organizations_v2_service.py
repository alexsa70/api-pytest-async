from __future__ import annotations

from clients.api_client import APIClient
from models.organization_models import OrganizationCreateRequest
from models.organization_v2_models import (
    OrganizationV2CreateResponse,
    OrganizationV2GetResponse,
    OrganizationV2PatchRequest,
    OrganizationV2PatchResponse,
)
from utils.endpoints import ORGANIZATION_BY_ID, ORGANIZATIONS


class OrganizationsV2Service:
    def __init__(self, api_client: APIClient) -> None:
        self.api_client = api_client

    async def create_organization(self, payload: OrganizationCreateRequest) -> OrganizationV2CreateResponse:
        response = await self.api_client.post(
            ORGANIZATIONS,
            json=payload.model_dump(by_alias=True),
            expected_status=200,
        )
        return OrganizationV2CreateResponse.model_validate(response.json())

    async def get_organization(self, organization_id: int) -> OrganizationV2GetResponse:
        response = await self.api_client.get(
            ORGANIZATION_BY_ID.format(org_id=organization_id),
            expected_status=200,
        )
        return OrganizationV2GetResponse.model_validate(response.json())

    async def patch_organization(
        self,
        organization_id: int,
        payload: OrganizationV2PatchRequest,
    ) -> OrganizationV2PatchResponse:
        response = await self.api_client.patch(
            ORGANIZATION_BY_ID.format(org_id=organization_id),
            json=payload.model_dump(by_alias=True, exclude_none=True),
            expected_status=200,
        )
        return OrganizationV2PatchResponse.model_validate(response.json())
