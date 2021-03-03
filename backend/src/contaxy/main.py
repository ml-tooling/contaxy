from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from contaxy.auth import Authenticator, Token
from contaxy.users import User
from contaxy.utils.api_utils import patch_fastapi

from .dependencies import get_authenticated_user, get_authenticator

app = FastAPI()


@app.post("/login")
def login_oauth(
    data: OAuth2PasswordRequestForm = Depends(),
    auth: Authenticator = Depends(get_authenticator),
) -> Token:
    user = auth.authenticate_user(data.username, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth.create_access_token(user)
    return token


@app.get("/hello")
async def hello(auth_user: User = Depends(get_authenticated_user)):
    return {"message": f"Hello {auth_user.full_name}! The world is yours now!"}


@app.get("/echo")
async def echo(input: str, auth_user: User = Depends(get_authenticated_user)):
    return input


# Patch Fastapi to allow relative path resolution.
patch_fastapi(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app, host="0.0.0.0", port=8081, log_level="info"
    )  # cannot use reload=True anymore
