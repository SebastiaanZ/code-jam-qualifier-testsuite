import types
import unittest

import test_qualifier

from testsuite.runner import QualifierTestRunner


def load_testsuite(
    test_module: types.ModuleType,
    filename: str = "qualifier"
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


if __name__ == "__main__":
    test_suite = load_testsuite(test_qualifier, "qualifier")
    runner = QualifierTestRunner(user="Ves Zappa", verbosity=2)
    runner.run(test_suite)
