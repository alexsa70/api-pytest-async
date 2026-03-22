from __future__ import annotations

from clients.api_client import APIClient
from models.devices.models import DevicePatchRequest, DeviceGetResponse
from utils.endpoints import DEVICE_BY_IMEI


class DevicesService:
    def __init__(self, api_client: APIClient) -> None:
        self.api_client = api_client

    async def get_device(self, imei: str) -> DeviceGetResponse:
        response = await self.api_client.get(
            DEVICE_BY_IMEI.format(imei=imei),
            expected_status=200,
        )
        return DeviceGetResponse.model_validate(response.json())

    async def patch_device(self, imei: str, payload: DevicePatchRequest) -> None:
        await self.api_client.patch(
            DEVICE_BY_IMEI.format(imei=imei),
            json=payload.model_dump(by_alias=True, exclude_none=True),
            expected_status=200,
        )
