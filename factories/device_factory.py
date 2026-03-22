from __future__ import annotations

from faker import Faker

from models.devices.models import DevicePatchRequest

class DeviceFactory:
    def __init__(self, faker_instance: Faker) -> None:
        self.faker = faker_instance

    def build_patch_request(self) -> DevicePatchRequest:
        return DevicePatchRequest(
            name=f"Device-{self.faker.lexify(text='??????')}",
            enabled=True,
        )
