from typing import Generator

from fastapi import HTTPException, Request, Security
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.api_key import APIKeyCookie, APIKeyHeader, APIKeyQuery
from starlette import status

from contaxy import config
from contaxy.managers.components import ComponentManager


def get_api_token(
    api_token_query: str = Security(
        APIKeyQuery(name=config.API_TOKEN_NAME, auto_error=False)
    ),
    api_token_header: str = Security(
        APIKeyHeader(name=config.API_TOKEN_NAME, auto_error=False)
    ),
    api_token_cookie: str = Security(
        APIKeyCookie(name=config.API_TOKEN_NAME, auto_error=False)
    ),
    bearer_token: str = Security(
        OAuth2PasswordBearer(tokenUrl="auth/oauth/token", auto_error=False)
    ),
) -> str:
    # TODO: already check token validity here?
    if api_token_query:
        return api_token_query
    elif api_token_header:
        return api_token_header
    elif api_token_cookie:
        return api_token_cookie
    elif bearer_token:
        return bearer_token
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No API token was provided.",
        )


def get_component_manager(request: Request) -> Generator[ComponentManager, None, None]:
    """Returns the initialized component manager.

    This is used as FastAPI dependency and called for every request.
    """
    with ComponentManager(request) as component_manager:
        yield component_manager
