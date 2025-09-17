from tn_sdk.utils.constants import DEFAULT_SDK_ERROR, INVALID_DATA_ERROR


class TnApiException(Exception):
    """
    Base class for all Trip Ninja SDK exceptions.

    :param message: Human-readable error message
    :param code: Optional error code (similar to API error codes)
    """

    def __init__(
        self,
        message: str = DEFAULT_SDK_ERROR.get("message"),
        code: str = DEFAULT_SDK_ERROR.get("code"),
    ):
        super().__init__(message)
        self.code = code
        self.message = message

    def __str__(self):
        return f"[{self.code}] {self.message}"


class InvalidDataException(TnApiException):
    """Raised when invalid or malformed data is passed to an SDK function."""

    def __init__(self, message: str = INVALID_DATA_ERROR.get("message")):
        super().__init__(message, code=INVALID_DATA_ERROR.get("code"))
