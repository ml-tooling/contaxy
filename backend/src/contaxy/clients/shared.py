from fastapi import status
from requests.models import Response

from contaxy.api.error_handling import UnifiedErrorFormat
from contaxy.schema import UnauthenticatedError
from contaxy.schema.exceptions import (
    ClientValueError,
    PermissionDeniedError,
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
)


def handle_errors(response: Response) -> None:
    if response.status_code < 400 and response.status_code >= 600:
        return

    message = None
    try:
        error = UnifiedErrorFormat.parse_raw(response.json())
        message = error.message
    except Exception:
        pass

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        raise UnauthenticatedError(message)

    if response.status_code == status.HTTP_403_FORBIDDEN:
        raise PermissionDeniedError(message)

    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise ResourceNotFoundError(message)

    if response.status_code == status.HTTP_409_CONFLICT:
        raise ResourceAlreadyExistsError(message)

    # TODO: already used
    # if response.status_code == status.HTTP_409_CONFLICT:
    #    raise ResourceUpdateFailedError(message)

    if response.status_code == status.HTTP_400_BAD_REQUEST:
        raise ClientValueError(message)
