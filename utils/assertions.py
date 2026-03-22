import httpx

from models.users.models import User, UserResponse


def assert_status_code(response: httpx.Response, expected_status: int) -> None:
    assert response.status_code == expected_status, (
        f"Unexpected status code: expected={expected_status}, actual={response.status_code}, body={response.text}"
    )


def assert_user_fields(user: User) -> None:
    assert user.id > 0
    assert "@" in user.email
    assert bool(user.first_name.strip())
    assert bool(user.last_name.strip())


def assert_user_response(model: UserResponse) -> None:
    assert_user_fields(model.data)
