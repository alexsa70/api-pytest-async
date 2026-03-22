from clients.api_client import APIClient
from models.auth.models import AuthLoginRequest, AuthTokenResponse
from utils.endpoints import AUTH_LOGIN


class AuthService:
    def __init__(self, api_client: APIClient) -> None:
        self.api_client = api_client

    async def login(self, payload: AuthLoginRequest) -> AuthTokenResponse:
        response = await self.api_client.post(
            AUTH_LOGIN,
            json=payload.model_dump(),
            expected_status=200,
        )
        return AuthTokenResponse.model_validate(response.json())
