from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException, RequestValidationError
from starlette.responses import JSONResponse, Response

from contaxy.schema.auth import OAuth2Error, OAuth2ErrorDetails
from contaxy.schema.exceptions import ClientBaseError, ProblemDetails


async def handel_http_exeptions(request: Request, exc: HTTPException) -> Response:

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


async def handle_validation_exception(
    request: Request, exc: RequestValidationError
) -> Response:
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
