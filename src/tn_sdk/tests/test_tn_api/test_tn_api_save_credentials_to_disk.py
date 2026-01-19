import json
from unittest.mock import MagicMock

from tn_sdk import TnApi
from tn_sdk.tests.test_tn_api.base_tn_api_test import BaseTnApiTest


class TestSaveCredentialsToDisk(BaseTnApiTest):

    def test_save_credentials_to_disk__valid_data__writes_to_temp_and_renames(self):

        api = TnApi()
        token_data = {"production": "token"}

        # Mock temp path
        mock_temp_path = MagicMock()
        self.mock_path_instance.with_suffix.return_value = mock_temp_path

        api._save_credentials_to_disk(token_data)

        # Verify write
        mock_temp_path.write_text.assert_called_once_with(
            json.dumps(token_data, indent=4), encoding="utf-8"
        )
        # Verify atomic rename
        mock_temp_path.replace.assert_called_once_with(self.mock_path_instance)

    def test_save_credentials_to_disk__os_error_occurs__silently_passes(self):

        api = TnApi()
        mock_temp_path = MagicMock()
        self.mock_path_instance.with_suffix.return_value = mock_temp_path
        mock_temp_path.write_text.side_effect = OSError("Permission denied")

        # Should not raise
        try:
            api._save_credentials_to_disk({})
        except OSError:
            self.fail("OSError should have been caught")
