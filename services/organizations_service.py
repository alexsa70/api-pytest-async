from __future__ import annotations

from clients.api_client import APIClient
from models.organization_models import OrganizationCreateRequest, OrganizationResponse
from utils.endpoints import ORGANIZATIONS


class OrganizationsService:
    def __init__(self, api_client: APIClient) -> None:
        self.api_client = api_client

    async def create_organization(self, payload: OrganizationCreateRequest) -> OrganizationResponse:
        response = await self.api_client.post(
            ORGANIZATIONS,
            json=payload.model_dump(by_alias=True),
            expected_status=201,
        )
        return OrganizationResponse.model_validate(response.json())
