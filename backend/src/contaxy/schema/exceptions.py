from typing import Any, Dict, Optional, Tuple

from fastapi import HTTPException, status


class ClientBaseError(HTTPException):
    """Basic exception class for all errors that should be shown to the client/user.

    The error details will be shown to the client (user) if it is not handled otherwise.
    """

    def __init__(
        self,
        status_code: int,
        message: str,
        explanation: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        """Initializes the exception.

        Args:
            status_code: The HTTP status code associated with the error.
            message: A short summary of the error.
            explanation (optional): A human readable explanation specific to this error that is helpful to locate the problem and give advice on how to proceed.
            metadata (optional): Additional problem details/metadata.
        """

        super(ClientBaseError, self).__init__(
            status_code=status_code,
            detail=message,
        )

        self.explanation = explanation
        self.metadata = metadata


class ServerBaseError(Exception):
    """Basic exception class for all server internal errors that should not be shown with details to the user.

    If the error is not handled, an `Internal Server Error` (Status Code 500) will be shown
    to the client (user) without any additional details. In this case, the execption will be
    automatically logged.
    """

    def __init__(
        self,
        args: Tuple[Any, ...],
    ):
        """Initializes the exception.

        Args:
            args: The tuple of arguments given to the exception constructor.
        """
        super(Exception, self).__init__(args)


class UnauthenticatedError(ClientBaseError):
    """Client error that indicates invalid, expired, or missing authentication credentials.

    The error message should contain specific details about the problem, e.g.:

    - No access token was provided.

    The error details will be shown to the client (user) if it is not handled otherwise.
    """

    _HTTP_STATUS_CODE = status.HTTP_401_UNAUTHORIZED
    _DEFAULT_MESSAGE = "Invalid authentication credentials."
    _DEFAULT_EXPLANATION = "This can happen because credentials or token are missing, expired, or otherwise invalid."

    def __init__(
        self,
        message: Optional[str] = None,
        explanation: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> None:
        """Initializes the error.

        Args:
            message (optional): A message shown to the user that overwrites the default message.
            explanation (optional): A human readable explanation specific to this error that is helpful to locate the problem and give advice on how to proceed.
            metadata (optional): Additional problem details/metadata.
        """
        super(UnauthenticatedError, self).__init__(
            status_code=UnauthenticatedError._HTTP_STATUS_CODE,
            message=message or UnauthenticatedError._DEFAULT_MESSAGE,
            explanation=explanation or UnauthenticatedError._DEFAULT_EXPLANATION,
            metadata=metadata,
        )


class PermissionDeniedError(ClientBaseError):
    """Client error that indicates that a client does not have sufficient permission for the request.

    The error message should contain specific details about the resource, e.g.:

    - Permission 'xxx' denied on resource 'yyy'.

    The error details will be shown to the client (user) if it is not handled otherwise.
    """

    _HTTP_STATUS_CODE = status.HTTP_403_FORBIDDEN
    _DEFAULT_MESSAGE = "The authorized user does not have sufficient permission."
    _DEFAULT_EXPLANATION = "This can happen because the token does not have the right scopes or the user doesn't have the required permission."

    def __init__(
        self,
        message: Optional[str] = None,
        explanation: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> None:
        """Initializes the error.

        Args:
            message (optional): A message shown to the user that overwrites the default message.
            explanation (optional): A human readable explanation specific to this error that is helpful to locate the problem and give advice on how to proceed.
            metadata (optional): Additional problem details/metadata.
        """
        super(PermissionDeniedError, self).__init__(
            status_code=PermissionDeniedError._HTTP_STATUS_CODE,
            message=message or PermissionDeniedError._DEFAULT_MESSAGE,
            explanation=explanation or PermissionDeniedError._DEFAULT_EXPLANATION,
            metadata=metadata,
        )


class ResourceNotFoundError(ClientBaseError):
    """Client error that indicates that a specified resource is not found.

    The error message should contain specific details about the resource, e.g.:

    - Resource 'xxx' not found.

    The error details will be shown to the client (user) if it is not handled otherwise.
    """

    _HTTP_STATUS_CODE = status.HTTP_404_NOT_FOUND
    _DEFAULT_MESSAGE = "A specified resource is not found."

    def __init__(
        self,
        message: Optional[str] = None,
        explanation: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> None:
        """Initializes the error.

        This error should be raised if

        Args:
            message (optional): A message shown to the user that overwrites the default message.
            explanation (optional): A human readable explanation specific to this error that is helpful to locate the problem and give advice on how to proceed.
            metadata (optional): Additional problem details/metadata.
        """
        super(ResourceNotFoundError, self).__init__(
            status_code=ResourceNotFoundError._HTTP_STATUS_CODE,
            message=message or ResourceNotFoundError._DEFAULT_MESSAGE,
            explanation=explanation,
            metadata=metadata,
        )


class ResourceAlreadyExistsError(ClientBaseError):
    """Client error that indicates that a resource that a client tried to create already exists.

    The error message should contain specific details about the problem and resource, e.g.:

    - Resource 'xxx' already exists.
    - Couldn’t acquire lock on resource ‘xxx’.

    The error details will be shown to the client (user) if it is not handled otherwise.
    """

    _HTTP_STATUS_CODE = status.HTTP_409_CONFLICT
    _DEFAULT_MESSAGE = "The resource already exists."

    def __init__(
        self,
        message: Optional[str] = None,
        explanation: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> None:
        """Initializes the error.

        Args:
            message (optional): A message shown to the user that overwrites the default message.
            explanation (optional): A human readable explanation specific to this error that is helpful to locate the problem and give advice on how to proceed.
            metadata (optional): Additional problem details/metadata.
        """
        super(ResourceAlreadyExistsError, self).__init__(
            status_code=ResourceAlreadyExistsError._HTTP_STATUS_CODE,
            message=message or ResourceAlreadyExistsError._DEFAULT_MESSAGE,
            explanation=explanation,
            metadata=metadata,
        )


class ClientValueError(ClientBaseError, ValueError):
    """Client error that indicates that the client input is invalid.

    The error message should contain specific details about the problem, e.g.:

    - Request field x.y.z is xxx, expected one of [yyy, zzz].
    - Parameter 'age' is out of range [0, 125].

    The error details will be shown to the client (user) if it is not handled otherwise.
    """

    _HTTP_STATUS_CODE = status.HTTP_400_BAD_REQUEST
    _DEFAULT_MESSAGE = "An invalid argument was specified by the client. "

    def __init__(
        self,
        message: Optional[str] = None,
        explanation: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> None:
        """Initializes the error.

        Args:
            message (optional): A message shown to the user that overwrites the default message.
            explanation (optional): A human readable explanation specific to this error that is helpful to locate the problem and give advice on how to proceed.
            metadata (optional): Additional problem details/metadata.
        """
        super(ClientValueError, self).__init__(
            status_code=ClientValueError._HTTP_STATUS_CODE,
            message=message or ClientValueError._DEFAULT_MESSAGE,
            explanation=explanation,
            metadata=metadata,
        )
