from fastapi import FastAPI

from contaxy.utils.api_utils import patch_fastapi

from .routers import auth, users

app = FastAPI()
app.include_router(users.router)
app.include_router(auth.router)


# Patch Fastapi to allow relative path resolution.
patch_fastapi(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app, host="0.0.0.0", port=8081, log_level="info"
    )  # cannot use reload=True anymore
