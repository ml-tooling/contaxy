from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic.types import SecretStr

from ..dependencies import get_auth_manager
from ..exceptions import AuthenticationError
from ..managers.auth import AuthManager, LoginForm, Token
from ..models.users import UserIn, UserOut

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/register")
def register(
    login_data: LoginForm = Depends(),
    auth_manager: AuthManager = Depends(get_auth_manager),
) -> UserOut:

    user_data = {
        "username": login_data.username,
        "password": SecretStr(login_data.password),
    }

    if login_data.email:
        user_data.update({"email": login_data.email})
    if login_data.display_name:
        user_data.update({"display_name": login_data.display_name})

    user = UserIn(**user_data)

    try:
        # ? Shall the user be logged in directly in
        new_user = auth_manager.register_user(user)
        return new_user
    except AuthenticationError as e:
        status_code = (
            status.HTTP_403_FORBIDDEN
            if e.reason == AuthenticationError.USER_REGISTRATION_DEACTIVATED
            else status.HTTP_409_CONFLICT
        )
        raise HTTPException(status_code, e.msg)


@router.post(
    "/login",
)
def login_oauth(
    data: OAuth2PasswordRequestForm = Depends(),
    authenticator: AuthManager = Depends(get_auth_manager),
) -> Token:
    try:
        return authenticator.authenticate_user(data.username, SecretStr(data.password))
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.msg,
        )
