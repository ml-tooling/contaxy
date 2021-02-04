from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.param_functions import Form
from fastapi.security import OAuth2PasswordRequestForm
from pydantic.networks import EmailStr
from pydantic.types import SecretStr

from contaxy.auth import Authenticatable, AuthManager, Token
from contaxy.exceptions import AuthenticationError
from contaxy.user import User, UserIn
from contaxy.utils.api_utils import patch_fastapi

from .dependencies import get_auth_manager, get_authenticatable, get_authenticated_user

app = FastAPI()


@app.post("/auth/register")
def register(
    username: str = Form(...),
    password: str = Form(...),
    email: Optional[str] = Form(None),
    display_name: Optional[str] = Form(None),
    auth_manager: AuthManager = Depends(get_auth_manager),
) -> User:

    user_data = {"username": username, "password": SecretStr(password)}

    if email:
        user_data.update({"email": EmailStr(email)})
    if display_name:
        user_data.update({"display_name": display_name})

    user = UserIn(**user_data)

    try:
        # ? Shall the user be logged in directly in
        return auth_manager.register_user(user)
    except AuthenticationError as e:
        status_code = (
            status.HTTP_403_FORBIDDEN
            if e.reason == AuthenticationError.USER_REGISTRATION_DEACTIVATED
            else status.HTTP_409_CONFLICT
        )
        raise HTTPException(status_code, e.msg)


@app.post(
    "/auth/login",
)
def login_oauth(
    data: OAuth2PasswordRequestForm = Depends(),
    authenticator: AuthManager = Depends(get_auth_manager),
) -> Token:
    user = authenticator.authenticate_user(data.username, SecretStr(data.password))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = authenticator.create_access_token(user)
    return token


@app.get("/hello")
async def hello(user: User = Depends(get_authenticated_user)):
    return {"message": f"Hello {user.display_name}! The world is yours now!"}


@app.get("/hello-auth")
async def hello_auth(auth: Authenticatable = Depends(get_authenticatable)):
    return {"message": f"Hello! Your ID is { auth.id }!"}


# Patch Fastapi to allow relative path resolution.
patch_fastapi(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app, host="0.0.0.0", port=8081, log_level="info"
    )  # cannot use reload=True anymore
