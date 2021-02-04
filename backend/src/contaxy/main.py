from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from contaxy.auth import Authenticatable, AuthenticationManager, Token
from contaxy.user import User
from contaxy.utils.api_utils import patch_fastapi

from .dependencies import get_authenticatable, get_authenticated_user, get_authenticator

app = FastAPI()


@app.post(
    "/auth/login",
)
def login_oauth(
    data: OAuth2PasswordRequestForm = Depends(),
    authenticator: AuthenticationManager = Depends(get_authenticator),
) -> Token:
    user = authenticator.authenticate_user(data.username, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
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
