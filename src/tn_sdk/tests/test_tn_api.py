import unittest

from tn_sdk import TnApi
from tn_sdk.utils.constants import SANDBOX_API_URL, PRODUCTION_API_URL


class TestTnApi(unittest.TestCase):
    def setUp(self):
        """Create a reusable client instance for tests."""
        self.api_sandbox = TnApi("abc123", "refresh456", is_sandbox=True)
        self.api_prod = TnApi("abc123", "refresh456", is_sandbox=False)

    def test_tn_api__instantiate_sandbox__returns_api_details(self):
        self.assertEqual(self.api_sandbox._access_token, "abc123")
        self.assertEqual(self.api_sandbox._refresh_token, "refresh456")
        self.assertEqual(self.api_sandbox.base_url, SANDBOX_API_URL)

    def test_tn_api__instantiate_prod__returns_api_details(self):
        self.assertEqual(self.api_prod._access_token, "abc123")
        self.assertEqual(self.api_prod._refresh_token, "refresh456")
        self.assertEqual(self.api_prod.base_url, PRODUCTION_API_URL)
