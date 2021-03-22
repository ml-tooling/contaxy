from typing import List

import pytest
import requests
from faker import Faker

from contaxy.schema import User, UserInput

FAKER = Faker()


def _generate_user_data(users_to_generate: int) -> List[UserInput]:
    generated_users: List[UserInput] = []
    for _ in range(users_to_generate):
        # TODO: Also some with missing emails/usernames?
        generated_users.append(
            UserInput(username=FAKER.user_name(), email=FAKER.email())
        )
    return generated_users


@pytest.mark.integration
class TestUserEndpoints:
    def test_create_user(self, client: requests.Session) -> None:
        users_to_create = _generate_user_data(5)
        for user_to_create in users_to_create:
            response = client.post("/users", json=user_to_create.dict())
            created_user = User.parse_raw(response.json())
            assert created_user.username == created_user.username
            assert created_user.email == created_user.email
        assert response.status_code == 200

    def test_list_users(self, client: requests.Session, admin_token: str) -> None:
        client.headers.update({"authorization": admin_token})
        response = client.get("/users")
        assert response.status_code == 200
