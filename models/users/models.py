from pydantic import BaseModel, ConfigDict, Field


class UserCreateRequest(BaseModel):
    email: str
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)


class User(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int = Field(ge=1)
    email: str
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    is_active: bool = True


class UserResponse(BaseModel):
    data: User


class UserListResponse(BaseModel):
    data: list[User]
    total: int = Field(ge=0)
