from typing import Optional


class ContaxyBaseError(Exception):
    """Basic exception class for `contaxy` library errors."""

    def __init__(self, msg: str, predecessor_excp: Optional[Exception] = None):
        """Constructor method.

        Args:
            msg: The error message.
            predecessor_excp: Optionally, a predecessor exception can be passed on.
        """
        self.msg = msg
        self.predecessor_excp = predecessor_excp
        super().__init__(str(self))

    def __str__(self) -> str:
        if self.predecessor_excp:
            return self.msg + " Predecessor Exception: " + str(self.predecessor_excp)
        return self.msg


class AuthenticationError(ContaxyBaseError):

    USERNAME_EXISTS = 1
    EMAIL_EXISTS = 2
    USER_REGISTRATION_DEACTIVATED = 3
    USER_REGISTRATION_FAILED = 4
    UNKNOWN_USERNAME = 5
    INCORRECT_PASSWORD = 6

    def __init__(self, reason: int, predecessor_excp: Optional[Exception] = None):
        self.reason = reason
        super().__init__(self._get_reason_msg(), predecessor_excp)

    def _get_reason_msg(
        self,
    ) -> str:
        if self.reason == self.USERNAME_EXISTS:
            return "The username already exists"
        elif self.reason == self.EMAIL_EXISTS:
            return "The email is already registered"
        elif self.reason == self.USER_REGISTRATION_DEACTIVATED:
            return "User registration is not active. Please contact your administrator."
        elif self.reason == self.USER_REGISTRATION_FAILED:
            return "User registration failed"
        elif self.reason == self.UNKNOWN_USERNAME:
            return "Unknown username"
        elif self.reason == self.INCORRECT_PASSWORD:
            return "Incorrect password"
        else:
            return "Authorization error"
