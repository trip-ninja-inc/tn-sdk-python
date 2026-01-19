import json
import os
import zlib
from base64 import b64encode
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from tn_sdk.core.enums import TokenType
from tn_sdk.exceptions.exceptions import (
    InvalidDataException,
    TnAuthenticationFailedException,
)
from tn_sdk.utils.constants import (
    PRODUCTION_API_URL,
    SDK_AUTH_ENDPOINT,
    DEFAULT_COMPRESSION_LEVEL,
)
from tn_sdk.utils.validators import is_valid_base_url


class TnApi:
    """
    The entrypoint to the Trip Ninja SDK. Exposes useful functionality of the Trip Ninja API to the end user.
    """

    _GZIP_DEFAULT_COMPRESSION_LEVEL: int = DEFAULT_COMPRESSION_LEVEL

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        credential_file_path: str = "credentials.json",
        *,
        tn_api_url: str = PRODUCTION_API_URL,
        timeout: int = 30,
    ):
        """
        Initializes the SDK client.

        :param client_id: API Client ID (defaults to env TN_SDK_CLIENT_ID)
        :param client_secret: API Client Secret (defaults to env TN_SDK_CLIENT_SECRET)
        :param credential_file_path: Credentials file path (defaults to credentials.json)
        :keyword tn_api_url: Base URL for the API (defaults to the production API URL)
        :keyword timeout: Default timeout for network requests in seconds (defaults to 30)
        """
        self._tn_api_url = tn_api_url.rstrip("/")
        self._client_id = client_id or os.getenv("TN_SDK_CLIENT_ID", "")
        self._client_secret = client_secret or os.getenv("TN_SDK_CLIENT_SECRET", "")
        self._credential_file_path = Path(
            credential_file_path or "credentials.json"
        ).resolve()
        self._timeout = timeout

        # Validate that the client_id and secret exist (non-empty values)
        if not self._client_id or not self._client_secret:
            raise ValueError("Client ID and Client Secret are required.")

        # Validate that the directory of the credentials file exists
        parent_dir = self._credential_file_path.parent
        if not parent_dir.exists():
            raise FileNotFoundError(
                f"Credential file Directory: {parent_dir} not found."
            )

        # Validate the given tn_api_url
        if not is_valid_base_url(self._tn_api_url):
            raise ValueError("Invalid API URL.")

        # Request Session setup
        self.session = requests.Session()
        self._configure_network_retries()

        # Try to load token from file immediately on init
        self._credentials = self._load_token_from_disk()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        """
        Closes the SDK client's session.
        """
        self.session.close()

    def _configure_network_retries(self):
        """Configures retries for network blips (not 401s)."""
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _load_token_from_disk(self) -> dict:
        """
        Reads the credential file safely.
        Returns the credentials as a dictionary. Or an empty dictionary if no credentials are found.
        """
        if not self._credential_file_path.exists():
            return {}

        try:
            text = self._credential_file_path.read_text(encoding="utf-8")
            data = json.loads(text)
            return data
        except (json.JSONDecodeError, OSError):
            # If file is corrupt or unreadable, ignore it and treat as no credentials
            return {}

    def _save_credentials_to_disk(self, token_data: dict) -> None:
        """
        Writes credentials to disk ATOMICALLY.
        This prevents partial writes if the process crashes or two processes write at once.

        :param token_data: Token data
        """
        temp_path = self._credential_file_path.with_suffix(".tmp")
        try:
            temp_path.write_text(json.dumps(token_data, indent=4), encoding="utf-8")

            temp_path.replace(self._credential_file_path)
        except OSError:
            # If we lack permissions, we just skip saving but keep the token in memory
            pass

    def _fetch_new_credentials_from_api(self) -> str:
        """
        Calls the API to get the latest credentials.
        """
        headers = {
            "Content-Type": "application/json",
            "X-Client-ID": self._client_id,
            "X-Client-Secret": self._client_secret,
        }
        url = f"{self._tn_api_url}{SDK_AUTH_ENDPOINT}"

        try:
            response = self.session.post(
                url=url, headers=headers, timeout=self._timeout
            )
            response.raise_for_status()

            data = response.json()

            if not data:
                raise TnAuthenticationFailedException("Invalid API Response")

            self._save_credentials_to_disk(data)
            return data

        except requests.exceptions.RequestException as err:
            msg = "Authentication failed"
            if err.response is not None:
                msg += f": {err.response.text}"
            raise TnAuthenticationFailedException(msg) from err

    def _request(
        self,
        method: str,
        endpoint: str,
        token_type: TokenType = TokenType.PRODUCTION,
        **kwargs,
    ) -> dict:
        """
        Central internal request handler

        Handles:
        - Refreshing token
        - Setting headers
        - Parsing the response JSON

        :param method: HTTP method
        :param endpoint: API endpoint
        :param token_type: The TokenType to use for this specific request (defaults to production)
        :param kwargs: Any additional kwargs to pass to the request

        :return: JSON response
        """
        if not self._credentials:
            self._credentials = self._fetch_new_credentials_from_api()

        url = f"{self._tn_api_url}{endpoint}"
        token = self._credentials[token_type.value]

        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Token {token}"
        kwargs["headers"] = headers

        response = self.session.request(method, url, timeout=self._timeout, **kwargs)

        if response.status_code == 401:
            # Token expired.
            disk_token = self._load_token_from_disk()

            if disk_token and disk_token != self._credentials:
                self._credentials = disk_token
            else:
                self._credentials = self._fetch_new_credentials_from_api()

            # Retry the request with the new token
            token = self._credentials[token_type.value]
            headers["Authorization"] = f"Token {token}"
            kwargs["headers"] = headers
            response = self.session.request(
                method, url, timeout=self._timeout, **kwargs
            )

        response.raise_for_status()
        return response.json()

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

    def authenticate(self) -> None:
        """
        Retrieves and stores the latest tokens from the API
        :return: None (updates the file and state in place)
        """
        self._fetch_new_credentials_from_api()
