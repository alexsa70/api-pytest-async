from clients.api_client import APIClient
from models.user_models import UserCreateRequest, UserListResponse, UserResponse
from utils.endpoints import USER_BY_ID, USERS


class UsersService:
    def __init__(self, api_client: APIClient) -> None:
        self.api_client = api_client

    async def get_user(self, user_id: int) -> UserResponse:
        response = await self.api_client.get(USER_BY_ID.format(user_id=user_id), expected_status=200)
        return UserResponse.model_validate(response.json())

    async def list_users(self) -> UserListResponse:
        response = await self.api_client.get(USERS, expected_status=200)
        return UserListResponse.model_validate(response.json())

    async def create_user(self, payload: UserCreateRequest) -> UserResponse:
        response = await self.api_client.post(USERS, json=payload.model_dump(), expected_status=201)
        return UserResponse.model_validate(response.json())
