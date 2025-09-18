import json
import zlib
from base64 import b64encode

from tn_sdk.exceptions.exceptions import InvalidDataException
from tn_sdk.utils.constants import (
    SANDBOX_API_URL,
    PRODUCTION_API_URL,
    DEFAULT_COMPRESSION_LEVEL,
)


class TnApi:
    """
    The entrypoint to the Trip Ninja SDK. Exposes useful functionality of the Trip Ninja API to the end user.
    """

    _TN_BASE_PROD_URL: str = PRODUCTION_API_URL
    _TN_BASE_SANDBOX_URL: str = SANDBOX_API_URL
    _GZIP_DEFAULT_COMPRESSION_LEVEL: int = DEFAULT_COMPRESSION_LEVEL

    def __init__(self, access_token: str, refresh_token: str, is_sandbox: bool = False):
        """
        Initializes and instantiates the SDK client.

        :param access_token: The token provided by the Admin Panel that is used to gain access to the API.
        :param refresh_token: The token provided by the Admin Panel that is used to refresh a user's access token.
        :param is_sandbox: Whether the client is connecting to the sandbox or the production environment.
        """
        self._access_token: str = access_token
        self._refresh_token: str = refresh_token
        self.base_url: str = (
            self._TN_BASE_SANDBOX_URL if is_sandbox else self._TN_BASE_PROD_URL
        )

    def prepare_data_for_generate_solutions(self, json_data: str) -> bytes:
        """
        This function prepares the data for generating solutions by compressing the data

        :param json_data: JSON encoded data
        :return: compressed bytes
        """

        if not isinstance(json_data, str):
            raise InvalidDataException("Input must be a JSON-encoded string")

        compressed_data = zlib.compress(
            json_data.encode("utf-8"), level=self._GZIP_DEFAULT_COMPRESSION_LEVEL
        )
        encoded_compressed_response = b64encode(compressed_data)
        return encoded_compressed_response
