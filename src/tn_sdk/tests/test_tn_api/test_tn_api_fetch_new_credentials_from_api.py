from unittest.mock import MagicMock, patch

from requests import Response, HTTPError

from tn_sdk import TnApi
from tn_sdk.exceptions.exceptions import TnAuthenticationFailedException
from tn_sdk.tests.test_tn_api.base_tn_api_test import BaseTnApiTest


class TestFetchNewCredentialsFromApi(BaseTnApiTest):

    def test_fetch_new_credentials_from_api__api_call_succeeds__returns_data_and_saves_to_disk(
        self,
    ):
        api = TnApi()
        expected_data = {"production": "new_token"}

        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = expected_data
        self.mock_session_instance.post.return_value = mock_response

        with patch.object(api, "_save_credentials_to_disk") as mock_save:
            result = api._fetch_new_credentials_from_api()

            self.assertEqual(result, expected_data)
            mock_save.assert_called_once_with(expected_data)

    def test_fetch_new_credentials_from_api__api_call_fails__raises_tn_authentication_exception(
        self,
    ):
        api = TnApi()

        mock_response = MagicMock(spec=Response)
        mock_response.raise_for_status.side_effect = HTTPError("Boom")
        self.mock_session_instance.post.return_value = mock_response

        with self.assertRaises(TnAuthenticationFailedException):
            api._fetch_new_credentials_from_api()
