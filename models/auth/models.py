from pydantic import BaseModel, Field


class AuthLoginRequest(BaseModel):
    email: str = Field(min_length=1)
    password: str = Field(min_length=1)


class AuthTokenData(BaseModel):
    token: str = Field(min_length=1)
    organization_id: int | None = Field(default=None, alias="organizationId")


class AuthTokenResponse(BaseModel):
    # Mock auth response format
    access_token: str | None = Field(default=None, min_length=1)
    token_type: str = Field(default="Bearer")
    expires_in: int | None = Field(default=None, ge=1)

    # Stage2 v2 auth response format
    data: AuthTokenData | None = None

    @property
    def token(self) -> str:
        if self.access_token:
            return self.access_token
        if self.data and self.data.token:
            return self.data.token
        raise ValueError("Auth token is missing in response payload")

    @property
    def ttl_seconds(self) -> int:
        # v2 token docs mention 24 hours validity.
        return self.expires_in if self.expires_in is not None else 24 * 60 * 60
