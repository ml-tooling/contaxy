import traceback

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException, RequestValidationError
from loguru import logger
from starlette.responses import JSONResponse, Response

from contaxy.config import settings
from contaxy.schema.auth import OAuth2Error, OAuth2ErrorDetails
from contaxy.schema.exceptions import ClientBaseError, ProblemDetails


async def handle_http_exception(exc: HTTPException) -> Response:
    if settings.DEBUG:
        # Only log client errors in debug mode
        logger.opt(exception=exc).error(
            f"HTTP exception {type(exc).__name__} caught! Status code: {exc.status_code}"
        )

    if isinstance(exc, OAuth2Error):
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder(OAuth2ErrorDetails(error=exc.detail)),
        )

    problem_details = ProblemDetails(code=exc.status_code, message=exc.detail)

    if isinstance(exc, ClientBaseError):
        if exc.explanation:  # type: ignore
            problem_details.explanation = exc.explanation  # type: ignore

        if exc.metadata:  # type: ignore
            problem_details.details = exc.metadata  # type: ignore

    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(
            problem_details.dict(exclude_unset=True, exclude_defaults=True)
        ),
    )


async def handle_validation_exception(exc: RequestValidationError) -> Response:
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    details = exc.errors()
    message = "Validation Error."
    try:
        message = details[0]["msg"]
    except Exception:
        pass

    problem_details = ProblemDetails(code=status_code, message=message, details=details)

    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(
            problem_details.dict(exclude_unset=True, exclude_defaults=True)
        ),
    )


async def handle_server_exception(exc: Exception) -> Response:
    # Always log server exceptions
    logger.opt(exception=exc).error(f"Server exception {type(exc).__name__} caught!")
    problem_details = ProblemDetails(code=500, message="Internal server error!")
    if settings.DEBUG:
        # Only provide additional information for internal server errors when in debug mode
        exec_details = traceback.format_exc().splitlines()
        problem_details.message = f"Unhandled server exception {exec_details[-1]}"
        problem_details.details = exec_details
    return JSONResponse(
        status_code=500,
        content=jsonable_encoder(
            problem_details.dict(exclude_unset=True, exclude_defaults=True)
        ),
    )
