from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class OrganizationV2CreateResponse(BaseModel):
    organization_id: int = Field(alias="organizationId", ge=1)
    sso_secret: str = Field(alias="ssoSecret", min_length=1)
    request_id: str | None = Field(default=None, alias="requestId", min_length=1)

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class OrganizationV2PatchRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    exclusive_partner_only: bool | None = Field(default=None, alias="exclusivePartnerOnly")

    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class OrganizationV2PatchResponse(BaseModel):
    request_id: str = Field(alias="requestId", min_length=1)

    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class OrganizationV2Details(BaseModel):
    id: int = Field(ge=1)
    name: str = Field(min_length=1)
    exclusive_partner_only: bool = Field(alias="exclusivePartnerOnly")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class OrganizationV2GetResponse(BaseModel):
    data: OrganizationV2Details

    model_config = ConfigDict(extra="ignore")
