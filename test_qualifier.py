import collections
import datetime
import importlib
import unittest
import typing

from testsuite.testcase import QualifierTestCase

# from qualifier import parse_iso8601

TestCase = collections.namedtuple("TestCase", "input expected_output")


class Part001_BasicRequirements(QualifierTestCase):
    """Basic Requirements."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up the class by importing the right entry file."""
        super().setUpClass()
        cls.parse_iso8601 = staticmethod(cls.module.parse_iso8601)

    def _run_test_cases(self, test_cases: typing.Tuple[TestCase]) -> None:
        for test_case in test_cases:
            with self.subTest(**test_case._asdict()):
                actual_output = self.parse_iso8601(test_case.input)

                self.assertIsInstance(actual_output, datetime.datetime)
                self.assertEqual(test_case.expected_output, actual_output)

                # The strings for the basic requirements do not contain timezone information
                self.assertIsNone(actual_output.tzinfo)

    def test_001_accepts_valid_date_only_strings(self) -> None:
        """Parser parses valid date strings."""
        test_cases = (
            TestCase(
                input="1583-01-01",  # The standard only requires year 1583+ by default
                expected_output=datetime.datetime(year=1583, month=1, day=1)
            ),
            TestCase(
                input="2000-02-29",   # 2000 was a leap year, February 29 should be valid
                expected_output=datetime.datetime(year=2000, month=2, day=29)
            ),
            TestCase(
                input="2020-01-10",
                expected_output=datetime.datetime(year=2020, month=1, day=10)
            ),
            TestCase(
                input="9999-12-31",
                expected_output=datetime.datetime(year=9999, month=12, day=31)
            ),
            TestCase(
                input="2020-02-29",  # Another leap year
                expected_output=datetime.datetime(year=2020, month=2, day=29)
            ),
        )

        self._run_test_cases(test_cases)

    def test_002_accepts_valid_datetime_strings(self) -> None:
        """Parser parses valid datetime strings."""
        test_cases = (
            # <TIME> HH:MM:SS
            TestCase(
                input="2019-12-18T21:10:48",
                expected_output=datetime.datetime(
                    year=2019, month=12, day=18, hour=21, minute=10, second=48
                )
            ),
            TestCase(
                input="2028-02-29T00:00:00",  # Test for the range
                expected_output=datetime.datetime(
                    year=2028, month=2, day=29, hour=00, minute=00, second=00
                )
            ),
            TestCase(
                input="2399-08-31T23:59:59",  # The standard allows seconds=60; datetime does not
                expected_output=datetime.datetime(
                    year=2399, month=8, day=31, hour=23, minute=59, second=59
                )
            ),
            # <TIME> HH:MM
            TestCase(
                input="1956-01-31T08:17",
                expected_output=datetime.datetime(
                    year=1956, month=1, day=31, hour=8, minute=17
                )
            ),
            TestCase(
                input="1910-06-22T11:11",
                expected_output=datetime.datetime(
                    year=1910, month=6, day=22, hour=11, minute=11
                )
            ),
            TestCase(
                input="1905-12-22T23:59",
                expected_output=datetime.datetime(
                    year=1905, month=12, day=22, hour=23, minute=59
                )
            ),
            # <TIME> HH
            TestCase(
                input="1912-06-23T00",
                expected_output=datetime.datetime(
                    year=1912, month=6, day=23, hour=0
                )
            ),
            TestCase(
                input="1791-12-26T23",
                expected_output=datetime.datetime(
                    year=1791, month=12, day=26, hour=23
                )
            ),
            TestCase(
                input="1596-03-31T12",
                expected_output=datetime.datetime(
                    year=1596, month=3, day=31, hour=12
                )
            ),
        )

        self._run_test_cases(test_cases)

    def test_003_rejects_invalid_datetime_stings(self) -> None:
        """Parser raises ValueError for invalid datetime strings."""
        test_cases = (
            # Invalid date values in a valid format
            "2001-02-28",  # 2001 is not a leap year
            "1989-13-01",  # We don't have a 13th month
            "1990-01-32",  # January doesn't have 32 days
            "2345-2-10",  # MONTH should have two characters
            "1788-12-1",  # DAY should have two characters

            # Valid date values in an invalid format
            "2012/10/02",  # `/` is not a valid separator for dates
            "1999:10:02",  # `:` is not a valid separator for dates
            "2012 10 02",  # ` ` is not a valid separator
            "17-12-2019",  # DD-MM-YYYY is not an accepted format
            "90-03-14",  # YEAR should have four characters
            "2019-1012",  # Combining the normal and truncated format is not allowed
            "201910-12",  # Combining the normal and truncated format is not allowed

        )

        for invalid_datestring in test_cases:
            with self.subTest(input=invalid_datestring):
                with self.assertRaises(ValueError):
                    self.parse_iso8601(invalid_datestring)


class Part002_AdvancedRequirements(unittest.TestCase):
    """Advanced Requirements."""

    module_to_test = None

    @classmethod
    def setUpClass(cls) -> None:
        """Set up the class by importing the right entry file."""
        if not cls.module_to_test:
            cls.module_to_test = "qualifier"

        module = importlib.import_module(cls.module_to_test)
        cls.parse_iso8601 = staticmethod(module.parse_iso8601)

    def _run_test_cases(self, test_cases: typing.Tuple[TestCase]) -> None:
        for test_case in test_cases:
            with self.subTest(**test_case._asdict()):
                actual_output = self.parse_iso8601(test_case.input)

                self.assertIsInstance(actual_output, datetime.datetime)
                self.assertEqual(test_case.expected_output, actual_output)

                # The strings for the basic requirements do not contain timezone information
                self.assertIsNone(actual_output.tzinfo)

    def test_001_accepts_valid_date_only_strings(self) -> None:
        """Parser parses valid date strings."""
        test_cases = (
            TestCase(
                input="1583-01-01",  # The standard only requires year 1583+ by default
                expected_output=datetime.datetime(year=1583, month=1, day=1)
            ),
            TestCase(
                input="2000-02-29",   # 2000 was a leap year, February 29 should be valid
                expected_output=datetime.datetime(year=2000, month=2, day=29)
            ),
            TestCase(
                input="2020-01-10",
                expected_output=datetime.datetime(year=2020, month=1, day=10)
            ),
            TestCase(
                input="9999-12-31",
                expected_output=datetime.datetime(year=9999, month=12, day=31)
            ),
            TestCase(
                input="2020-02-29",  # Another leap year
                expected_output=datetime.datetime(year=2020, month=2, day=29)
            ),
        )

        self._run_test_cases(test_cases)
