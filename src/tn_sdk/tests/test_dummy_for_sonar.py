import unittest

class DummyTestForSonar(unittest.TestCase):
    def test_dummy_test__different_input__returns_not_equal(self):
        self.assertNotAlmostEqual(round(1.8), -1)
