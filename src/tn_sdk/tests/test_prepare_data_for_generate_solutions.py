import unittest
import zlib
from base64 import b64encode

from src.tn_sdk import TnApi
from src.tn_sdk.exceptions.exceptions import InvalidDataException


class TestPrepareDataForGenerateSolutions(unittest.TestCase):
    def setUp(self):
        """Create a reusable client instance for tests."""
        self.api_prod = TnApi("abc123", "refresh456", is_sandbox=False)

    def test_prepare_data_for_generate_solutions__valid_data__returns_bytes(self):
        input_data = '{"test": "value"}'
        result = self.api_prod.prepare_data_for_generate_solutions(input_data)

        expected = b64encode(
            zlib.compress(
                input_data.encode("utf-8"),
                level=self.api_prod._GZIP_DEFAULT_COMPRESSION_LEVEL,
            )
        )
        self.assertEqual(result, expected)
        self.assertIsInstance(result, bytes)

    def test_prepare_data_for_generate_solutions__invalid_data__returns_exception(self):
        # Passing invalid input should raise the Exception
        with self.assertRaises(InvalidDataException) as cm:
            self.api_prod.prepare_data_for_generate_solutions(None)

        self.assertIn("Failed to prepare data", str(cm.exception))
        self.assertEqual(cm.exception.code, "TN_INVALID_DATA")
