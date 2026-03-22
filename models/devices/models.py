from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DevicePatchRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    enabled: bool | None = None

    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class DeviceData(BaseModel):
    imei: str = Field(min_length=1)
    name: str = Field(min_length=1)
    enabled: bool

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

class DeviceGetResponse(BaseModel):
    data: DeviceData
    request_id: str | None = Field(default=None, alias="requestId")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")