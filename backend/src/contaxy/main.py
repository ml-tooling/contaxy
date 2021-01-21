from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from contaxy.utils.api_utils import patch_fastapi

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@app.get("/")
async def root() -> dict:
    return {"message": "Hello World"}


@app.post("/login")
def login_oauth(data: OAuth2PasswordRequestForm = Depends()):
    print(data)
    return {"access_token": "mytoken", "token_type": "bearer"}


# Patch Fastapi to allow relative path resolution.
patch_fastapi(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app, host="0.0.0.0", port=8081, log_level="info"
    )  # cannot use reload=True anymore
