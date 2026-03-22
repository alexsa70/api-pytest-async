from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class OrganizationCreateRequest(BaseModel):
    name: str = Field(min_length=1)
    exclusive_partner_only: bool = Field(alias="exclusivePartnerOnly", default=False)

    model_config = ConfigDict(populate_by_name=True)


class Organization(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int = Field(ge=1)
    name: str = Field(min_length=1)
    exclusive_partner_only: bool = Field(alias="exclusivePartnerOnly")

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class OrganizationResponse(BaseModel):
    data: Organization
