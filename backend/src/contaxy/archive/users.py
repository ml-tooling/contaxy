from typing import Dict, List, Optional

from pydantic import BaseModel

fake_users_db: Dict[str, dict] = {
    "admin": {
        "username": "admin",
        "email": "admin@mltooling.org",
        "password": "$2b$12$zzWEQiyZ6BWAprjS9Wg90eOA3QlS1nBrKWVhhNKGR9rSNaY0Z6JZ.",
        "scopes": ["admin"],
    },
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "password": "$2b$12$TMntBg236.H/HLDw/cIJY.pnE7JPBekI3Jlk5/Fb4Pq0ZRsr75hqG",
    },
    "hanspeter": {
        "username": "hanspeter",
        "full_name": "Hans Peter",
        "email": "hanspeter@example.com",
        "password": "$2b$12$trFr5B9mpkghxqsoM2C8jOjTMil37Ohpmhh9p2dsx0EssTdb75Mo.",
        "disabled": False,
    },
}


class User(BaseModel):
    username: str
    password: str
    email: Optional[str]
    full_name: Optional[str]
    scopes: List[str] = []


class UserManager:
    def get_user(self, username: str) -> Optional[User]:
        user_data = fake_users_db.get(username)
        if not user_data:
            return None
        return User(**user_data)
