from faker import Faker

from models.users.models import UserCreateRequest


class DataGenerator:
    def __init__(self, faker_instance: Faker | None = None) -> None:
        self.faker = faker_instance or Faker()

    def user_payload(self) -> dict[str, str]:
        payload = UserCreateRequest(
            email=self.faker.email(),
            first_name=self.faker.first_name(),
            last_name=self.faker.last_name(),
        )
        return payload.model_dump()

    def users_payload(self, count: int) -> list[dict[str, str]]:
        return [self.user_payload() for _ in range(count)]
