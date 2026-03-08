from faker import Faker

from models.user_models import User, UserCreateRequest


class UserFactory:
    def __init__(self, faker_instance: Faker | None = None) -> None:
        self.faker = faker_instance or Faker()

    def build_user_create_request(self) -> UserCreateRequest:
        return UserCreateRequest(
            email=self.faker.email(),
            first_name=self.faker.first_name(),
            last_name=self.faker.last_name(),
        )

    def build_user(self, user_id: int | None = None) -> User:
        request = self.build_user_create_request()
        return User(
            id=user_id or self.faker.random_int(min=1, max=100000),
            email=request.email,
            first_name=request.first_name,
            last_name=request.last_name,
            is_active=True,
        )

    def build_user_create_request_dict(self) -> dict[str, str]:
        return self.build_user_create_request().model_dump()
