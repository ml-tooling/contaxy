from fastapi import Depends, FastAPI

from .dependencies import get_authenticated_user
from .models.users import User
from .routers import auth, users
from .utils.api_utils import patch_fastapi

app = FastAPI()
app.include_router(users.router)
app.include_router(auth.router)


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
