# Test Template (Copy/Paste)

Используй этот шаблон для добавления нового endpoint-теста из `openapi.yaml`.

## 1) Endpoint constants (`utils/endpoints.py`)

```python
# Example: /devices/{imei}
DEVICE_BY_ID = "/devices/{imei}"
```

## 2) Models (`models/device_models.py`)

```python
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DevicePatchRequest(BaseModel):
    # Align with OpenAPI requestBody
    name: str | None = Field(default=None, min_length=1)
    enabled: bool | None = None

    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class DeviceData(BaseModel):
    # Align with OpenAPI response schema
    imei: str = Field(min_length=1)
    name: str = Field(min_length=1)
    enabled: bool

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class DeviceGetResponse(BaseModel):
    data: DeviceData
    request_id: str | None = Field(default=None, alias="requestId")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")
```

## 3) Service (`services/devices_service.py`)

```python
from __future__ import annotations

from clients.api_client import APIClient
from models.device_models import DeviceGetResponse, DevicePatchRequest
from utils.endpoints import DEVICE_BY_ID


class DevicesService:
    def __init__(self, api_client: APIClient) -> None:
        self.api_client = api_client

    async def get_device(self, imei: str) -> DeviceGetResponse:
        response = await self.api_client.get(
            DEVICE_BY_ID.format(imei=imei),
            expected_status=200,
        )
        return DeviceGetResponse.model_validate(response.json())

    async def patch_device(self, imei: str, payload: DevicePatchRequest) -> None:
        await self.api_client.patch(
            DEVICE_BY_ID.format(imei=imei),
            json=payload.model_dump(by_alias=True, exclude_none=True),
            expected_status=200,
        )
```

## 4) Factory (`factories/device_factory.py`)

```python
from __future__ import annotations

from faker import Faker

from models.device_models import DevicePatchRequest


class DeviceFactory:
    def __init__(self, faker_instance: Faker) -> None:
        self.faker = faker_instance

    def build_patch_request(self) -> DevicePatchRequest:
        return DevicePatchRequest(
            name=f"Device-{self.faker.lexify(text='??????')}",
            enabled=True,
        )
```

## 5) Fixtures (`tests/fixtures/data.py` + `tests/fixtures/api.py`)

`tests/fixtures/data.py`:

```python
import pytest
from factories.device_factory import DeviceFactory


@pytest.fixture
def device_factory(faker_instance):
    return DeviceFactory(faker_instance=faker_instance)
```

`tests/fixtures/api.py`:

```python
import pytest_asyncio
from services.devices_service import DevicesService


@pytest_asyncio.fixture
async def devices_service(api_client):
    return DevicesService(api_client)


@pytest_asyncio.fixture
async def integration_devices_service(integration_client):
    return DevicesService(integration_client)
```

## 6) Smoke test (`tests/smoke/test_devices_smoke.py`)

```python
from __future__ import annotations

import pytest

from services.devices_service import DevicesService


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_get_device_smoke(devices_service: DevicesService) -> None:
    # Use existing stable test IMEI for mock flow
    device = await devices_service.get_device("123456789012345")
    assert device.data.imei
```

## 7) Contract tests (`tests/contract/test_devices_contract.py`)

```python
from __future__ import annotations

import pytest

from models.device_models import DeviceGetResponse
from services.devices_service import DevicesService


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_device_contract(devices_service: DevicesService) -> None:
    response = await devices_service.get_device("123456789012345")
    reparsed = DeviceGetResponse.model_validate(response.model_dump(by_alias=True))
    assert reparsed.data.imei == response.data.imei
```

## 8) Negative tests (`tests/contract/test_devices_negative.py`)

```python
from __future__ import annotations

import pytest

from clients.api_client import APIClient
from utils.assertions import assert_status_code
from utils.endpoints import DEVICE_BY_ID


@pytest.mark.contract
@pytest.mark.negative
@pytest.mark.asyncio
async def test_get_device_401_without_token(settings, mock_transport) -> None:
    async with APIClient(
        base_url=settings.api_base_url,
        timeout=settings.api_timeout,
        transport=mock_transport,
    ) as raw_client:
        response = await raw_client.get(DEVICE_BY_ID.format(imei="123"))
    assert_status_code(response, 401)
```

## 9) Integration e2e (`tests/integration/test_devices_integration.py`)

```python
from __future__ import annotations

import pytest

from config.settings import Settings
from models.device_models import DevicePatchRequest
from services.devices_service import DevicesService


@pytest.mark.integration
@pytest.mark.skipif(not Settings().run_integration, reason="Set RUN_INTEGRATION=true for real API tests")
@pytest.mark.asyncio
async def test_real_api_device_e2e_read_modify_verify(
    integration_devices_service: DevicesService,
) -> None:
    imei = "REPLACE_WITH_REAL_TEST_IMEI"
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
        # Cleanup: rollback change even if assertion fails
        await integration_devices_service.patch_device(
            imei,
            DevicePatchRequest(name=original_name),
        )
```

## 10) Run

```bash
source .venv/bin/activate
pytest -m "smoke or contract" -n auto
pytest -m integration
pytest --alluredir=allure-results && allure serve allure-results
```

## Quick Checklist

- Endpoint + method + statuses совпадают с `openapi.yaml`.
- Все camelCase поля покрыты `alias`.
- Есть минимум: `smoke + contract + negative`.
- В `integration` есть cleanup в `finally`.
