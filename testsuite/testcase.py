import importlib
import types
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


def load_testsuite(
    test_module: types.ModuleType, filename: str = "qualifier"
) -> unittest.TestSuite:
    """
    Prepare a test suite to test a qualifier entry.

    The `test_module` should contain the test classes that we want use and `filename` should refer
    to the **importable** name of the solution we want to test.
    """
    test_loader = unittest.TestLoader()
    test_loader.sortTestMethodsUsing = None

    tests = []
    for name in dir(test_module):
        obj = getattr(test_module, name)
        if isinstance(obj, type) and issubclass(obj, unittest.TestCase):
            obj.module_to_test = filename
            tests.append(test_loader.loadTestsFromTestCase(obj))

    return unittest.TestSuite(tests)
