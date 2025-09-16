class TnApiException(Exception):
    """Base class for all Trip Ninja SDK exceptions."""

    def __init__(self, message: str, code: str = "TN_SDK_ERROR"):
        """
        :param message: Human-readable error message
        :param code: Optional error code (similar to API error codes)
        """
        super().__init__(message)
        self.code = code
        self.message = message

    def __str__(self):
        return f"[{self.code}] {self.message}"


class InvalidDataException(TnApiException):
    """Raised when invalid or malformed data is passed to an SDK function."""

    def __init__(self, message: str = "Invalid data provided for API request"):
        super().__init__(message, code="TN_INVALID_DATA")