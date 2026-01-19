import enum


class TokenType(enum.Enum):
    """
    Enum class to represent token types available to use for requests.

    The values represent the key of the token in the credentials.json
    """

    SANDBOX = "sandbox_token"
    PRODUCTION = "prod_token"
    DATA_STREAM = "data_stream_token"
