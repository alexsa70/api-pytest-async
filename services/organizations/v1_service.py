from __future__ import annotations

import httpx

from clients.api_client import APIClient
from utils.endpoints import V1_ORGANIZATION_BY_ID


class OrganizationsV1Service:
    def __init__(self, api_client: APIClient) -> None:
        self.api_client = api_client

    async def delete_organization(self, organization_id: int, token: str) -> None:
        response = await self.api_client.delete(
            V1_ORGANIZATION_BY_ID.format(org_id=organization_id),
            headers={
                "Authorization": token,
                "x-request-origin": "Admin Portal",
            },
        )
        if response.status_code not in (200, 204):
            raise httpx.HTTPStatusError(
                f"Expected status 200/204, got {response.status_code}",
                request=response.request,
                response=response,
            )
