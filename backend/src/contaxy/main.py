from fastapi import FastAPI

from contaxy.utils.api_utils import patch_fastapi

app = FastAPI()


@app.get("/")
async def root() -> dict:
    return {"message": "Hello World"}


# Patch Fastapi to allow relative path resolution.
patch_fastapi(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app, host="0.0.0.0", port=8081, log_level="info"
    )  # cannot use reload=True anymore
