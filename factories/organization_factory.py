from __future__ import annotations

from faker import Faker

from models.organization_models import OrganizationCreateRequest


class OrganizationFactory:
    def __init__(self, faker_instance: Faker | None = None) -> None:
        self.faker = faker_instance or Faker()

    def build_organization_create_request(
        self,
        *,
        exclusive_partner_only: bool = True,
    ) -> OrganizationCreateRequest:
        return OrganizationCreateRequest(
            name=self.faker.company(),
            exclusivePartnerOnly=exclusive_partner_only,
        )

    def build_organization_create_request_dict(
        self,
        *,
        exclusive_partner_only: bool = True,
    ) -> dict[str, object]:
        return self.build_organization_create_request(
            exclusive_partner_only=exclusive_partner_only,
        ).model_dump(by_alias=True)
