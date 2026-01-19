import unittest
from unittest.mock import MagicMock, patch


class BaseTnApiTest(unittest.TestCase):
    """
    Base class that handles all the common mocking setup.
    All tests that cover TnApi should inherit from this class.
    """

    def setUp(self):
        # Setup environmental variables
        self.env_patcher = patch.dict(
            "os.environ",
            {"TN_SDK_CLIENT_ID": "test_id", "TN_SDK_CLIENT_SECRET": "test_secret"},
        )
        self.env_patcher.start()

        # Patch the validator
        self.validator_patcher = patch(
            "tn_sdk.utils.validators.is_valid_base_url", return_value=True
        )
        self.mock_is_valid_url = self.validator_patcher.start()

        # Patch the Path constructor
        self.path_patcher = patch("tn_sdk.core.tn_api.Path")
        self.MockPath = self.path_patcher.start()

        # Patch path logic
        self.mock_path_instance = MagicMock()
        self.MockPath.return_value.resolve.return_value = self.mock_path_instance
        self.mock_path_instance.parent.exists.return_value = True
        self.mock_path_instance.exists.return_value = False

        # Mock the request session
        self.session_patcher = patch("requests.Session")
        self.MockSession = self.session_patcher.start()
        self.mock_session_instance = self.MockSession.return_value

    def tearDown(self):
        self.env_patcher.stop()
        self.validator_patcher.stop()
        self.path_patcher.stop()
        self.session_patcher.stop()
