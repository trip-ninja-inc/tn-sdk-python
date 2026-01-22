from unittest.mock import patch

from tn_sdk.tests.test_tn_api.base_tn_api_test import BaseTnApiTest
from tn_sdk import TnApi


class TestInit(BaseTnApiTest):

    def test_init__missing_client_id_or_secret__raises_value_error(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ValueError) as context:
                TnApi(client_id=None, client_secret=None)
            self.assertIn(
                "Client ID and Client Secret are required", str(context.exception)
            )

    def test_init__credential_directory_does_not_exist__raises_file_not_found_error(
        self,
    ):
        self.mock_path_instance.parent.exists.return_value = False

        with self.assertRaises(FileNotFoundError):
            TnApi()

    def test_init__invalid_api_url__raises_value_error(self):
        self.mock_is_valid_url.return_value = False

        with self.assertRaises(ValueError):
            TnApi(tn_api_url="bad_url")

    def test_init__valid_inputs__initializes_session_and_retries(self):
        api = TnApi()
        self.MockSession.assert_called_once()
        self.mock_session_instance.mount.assert_called()
        self.assertEqual(api._client_id, "test_id")
