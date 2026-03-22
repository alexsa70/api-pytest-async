from __future__ import annotations

import pytest

from config.settings import Settings
from models.devices.models import DevicePatchRequest
from services.devices.service import DevicesService


@pytest.mark.integration
@pytest.mark.skipif(not Settings().run_integration, reason="Set RUN_INTEGRATION=true for real API tests")
@pytest.mark.asyncio
async def test_real_api_device_e2e_read_modify_verify(
    integration_devices_service: DevicesService,
    settings: Settings,
) -> None:
    if not settings.test_device_imei:
        pytest.skip("Set TEST_DEVICE_IMEI in .env")
    imei = settings.test_device_imei
    original = await integration_devices_service.get_device(imei)
    original_name = original.data.name

    try:
        updated_name = f"{original_name}-upd"
        await integration_devices_service.patch_device(
            imei,
            DevicePatchRequest(name=updated_name),
        )
        updated = await integration_devices_service.get_device(imei)
        assert updated.data.name == updated_name
    finally:
        await integration_devices_service.patch_device(
            imei,
            DevicePatchRequest(name=original_name),
        )
