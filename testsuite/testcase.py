import importlib
import unittest


class QualifierTestCase(unittest.TestCase):
    """A custom test case that dynamically loads a module to test."""

    module_to_test = None

    @classmethod
    def setUpClass(cls) -> None:
        """Set up the class by importing the right entry file."""
        if not cls.module_to_test:
            cls.module_to_test = "qualifier_"

        cls.module = importlib.import_module(cls.module_to_test)
