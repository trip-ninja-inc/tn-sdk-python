import json

from tn_sdk import TnApi
from tn_sdk.tests.test_tn_api.base_tn_api_test import BaseTnApiTest


class TestLoadTokenFromDisk(BaseTnApiTest):

    def test_load_token_from_disk__file_does_not_exist__returns_empty_dict(self):
        self.mock_path_instance.exists.return_value = False
        api = TnApi()  # Init calls _load_token_from_disk internally

        # We call it again to test logic specifically
        result = api._load_token_from_disk()
        self.assertEqual(result, {})

    def test_load_token_from_disk__valid_json_file_exists__returns_dict(self):
        expected_data = {"production": "abc", "sandbox": "123"}
        self.mock_path_instance.exists.return_value = True
        self.mock_path_instance.read_text.return_value = json.dumps(expected_data)

        api = TnApi()
        result = api._load_token_from_disk()
        self.assertEqual(result, expected_data)

    def test_load_token_from_disk__corrupt_json_file__returns_empty_dict(self):
        self.mock_path_instance.exists.return_value = True
        self.mock_path_instance.read_text.return_value = "{ broken_json: "

        api = TnApi()
        result = api._load_token_from_disk()
        self.assertEqual(result, {})
