from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from faker import Faker

from config.settings import Settings
from factories.device_factory import DeviceFactory
from factories.organization_factory import OrganizationFactory
from factories.user_factory import UserFactory
from models.users.models import User


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings()


@pytest.fixture(scope="session")
def faker_instance() -> Faker:
    faker = Faker()
    Faker.seed(1234)
    return faker


@pytest.fixture
def organization_factory(faker_instance: Faker) -> OrganizationFactory:
    return OrganizationFactory(faker_instance=faker_instance)


@pytest.fixture(scope="session")
def organization_response_schema() -> dict[str, Any]:
    schema_path = Path("schemas/organization_schema.json")
    return json.loads(schema_path.read_text(encoding="utf-8"))


# Reference template fixtures for future user endpoints.
@pytest.fixture
def user_factory(faker_instance: Faker) -> UserFactory:
    return UserFactory(faker_instance=faker_instance)


@pytest.fixture(scope="session")
def user_response_schema() -> dict[str, Any]:
    schema_path = Path("schemas/user_schema.json")
    return json.loads(schema_path.read_text(encoding="utf-8"))


@pytest.fixture
def mock_users_store(user_factory: UserFactory) -> dict[int, User]:
    first = user_factory.build_user(user_id=1)
    second = user_factory.build_user(user_id=2)
    return {first.id: first, second.id: second}


@pytest.fixture
def device_factory(faker_instance: Faker) -> DeviceFactory:
    return DeviceFactory(faker_instance=faker_instance)
