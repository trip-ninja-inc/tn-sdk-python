import json
import zlib
from base64 import b64encode

from tn_sdk import TnApi
from tn_sdk.exceptions.exceptions import InvalidDataException
from tn_sdk.tests.test_tn_api.base_tn_api_test import BaseTnApiTest


class TestPrepareDataForGenerateSolutions(BaseTnApiTest):
    def setUp(self):
        """Create a reusable client instance for tests."""
        super().setUp()
        self.api_prod = TnApi(
            client_id="client_id",
            client_secret="client_secret",
        )

    def test_prepare_data_for_generate_solutions__valid_data__returns_bytes(self):
        input_data = {"test": "value"}
        result = self.api_prod.prepare_data_for_generate_solutions(
            json.dumps(input_data)
        )

        expected = b64encode(
            zlib.compress(
                json.dumps(input_data).encode("utf-8"),
                level=self.api_prod._GZIP_DEFAULT_COMPRESSION_LEVEL,
            )
        )
        self.assertEqual(result, expected)
        self.assertIsInstance(result, bytes)

    def test_prepare_data_for_generate_solutions__invalid_data__returns_exception(self):
        # Passing invalid input should raise a JSON exception
        with self.assertRaises(InvalidDataException) as cm:
            self.api_prod.prepare_data_for_generate_solutions(None)

        self.assertIn("Input must be a JSON-encoded string", str(cm.exception))
        self.assertEqual(cm.exception.code, "INVALID_DATA")
