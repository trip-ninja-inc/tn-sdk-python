from unittest.mock import MagicMock, patch

from tn_sdk import TnApi
from tn_sdk.core.enums import TokenType
from tn_sdk.tests.test_tn_api.base_tn_api_test import BaseTnApiTest


class TestRequest(BaseTnApiTest):

    def test_request__no_credentials_in_memory__fetches_new_credentials_before_request(
        self,
    ):
        api = TnApi()
        api._credentials = {}

        with patch.object(
            api, "_fetch_new_credentials_from_api", return_value={"prod_token": "fresh"}
        ) as mock_fetch:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"ok": True}
            self.mock_session_instance.request.return_value = mock_response

            api._request("GET", "/endpoint", TokenType.PRODUCTION)

            mock_fetch.assert_called_once()
            call_args = self.mock_session_instance.request.call_args
            self.assertEqual(call_args[1]["headers"]["Authorization"], "Token fresh")

    def test_request__401_returned__refreshes_from_api_and_retries(self):
        api = TnApi()
        api._credentials = {"prod_token": "stale"}

        # Logic: Disk is stale, API fetch required
        api._load_token_from_disk = MagicMock(return_value={"prod_token": "stale"})
        api._fetch_new_credentials_from_api = MagicMock(
            return_value={"prod_token": "fresh"}
        )

        # 1st call 401, 2nd call 200
        response_401 = MagicMock(status_code=401)
        response_200 = MagicMock(status_code=200)
        response_200.json.return_value = {}
        self.mock_session_instance.request.side_effect = [response_401, response_200]

        api._request("GET", "/test")

        api._fetch_new_credentials_from_api.assert_called_once()
        headers_second_call = self.mock_session_instance.request.call_args_list[1][1][
            "headers"
        ]
        self.assertEqual(headers_second_call["Authorization"], "Token fresh")

    def test_request__401_returned_and_disk_has_newer_token__uses_disk_token(self):
        api = TnApi()
        api._credentials = {"prod_token": "old_mem"}

        # Logic: Disk has NEWER token than memory
        api._load_token_from_disk = MagicMock(return_value={"prod_token": "newer_disk"})
        api._fetch_new_credentials_from_api = MagicMock()

        response_401 = MagicMock(status_code=401)
        response_200 = MagicMock(status_code=200)
        response_200.json.return_value = {}
        self.mock_session_instance.request.side_effect = [response_401, response_200]

        api._request("GET", "/test")

        api._fetch_new_credentials_from_api.assert_not_called()
        headers_second_call = self.mock_session_instance.request.call_args_list[1][1][
            "headers"
        ]
        self.assertEqual(headers_second_call["Authorization"], "Token newer_disk")
