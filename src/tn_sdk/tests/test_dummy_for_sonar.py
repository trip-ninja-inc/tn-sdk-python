import unittest

class DummyTestForSonar(unittest.TestCase):
    def test_dummy_test__different_input__returns_not_equal(self):
        self.assertNotEqual(round(1.5), 0)
