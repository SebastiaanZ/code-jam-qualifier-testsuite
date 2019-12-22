from __future__ import annotations

import dataclasses
import io
import math
import textwrap
import types
import typing
import unittest


TestOutcome = typing.Tuple[typing.Type[BaseException], BaseException, types.TracebackType]


class StreamWrapper:
    """Wrap an `io.TextIOBase` derived stream with utility methods."""

    def __init__(self, stream: io.TextIOBase, max_width: int = 100, verbosity: int = 0) -> None:
        self.stream = stream
        self.max_width = max_width
        self.verbosity = verbosity

    def __getattr__(self, attr: str) -> typing.Any:
        """Delegate attributes to the `io.TextIOBase` derived stream object."""
        return getattr(self.stream, attr)

    def fixed_width_text(self, text: str, width: int, placeholder: str = "...") -> str:
        """Create a string with a certain width from `text`."""
        text = textwrap.shorten(text, width=width, placeholder=placeholder)
        return f"{text:<{width}}"

    def writeln(self, text: str = "") -> None:
        """Write a line to the stream."""
        if text:
            text = textwrap.shorten(text, width=self.max_width, placeholder="...")
            self.stream.write(text)
        self.stream.write("\n")

    def write_separator(self, char: str = "-", length: typing.Optional[int] = None) -> None:
        """Write a separator line to the stream."""
        if not length:
            length = self.max_width
        multiplier = math.ceil(length / len(char))
        separator = char * multiplier
        self.writeln(separator[:self.max_width])

    def write_test_description(
        self,
        description: str,
        subtest_results: SectionResults,
    ) -> None:
        """Write a test description."""
        description_length = self.max_width - 23
        description = f"{description: <{description_length}}"
        self.write(description)
        if self.verbosity:
            passed, failed, total = subtest_results
            self.write(f"{passed:>3} {failed:>3} {total:>3}    ")
        else:
            self.write(" " * 15)

    def write_subtest_failure(self, subtest: unittest.TestCase, outcome: TestOutcome) -> None:
        """Format subtest failure and write it to the stream."""
        self.writeln()
        self.write_separator("-")
        self.writeln("Failing test case:")

        kwargs = subtest.params
        if "input" in kwargs:
            self.write(f"  Input:             {kwargs['input']}\n")
        if "expected_output" in kwargs:
            self.write(f"  Expected output:   {repr(kwargs['expected_output'])}\n")

        _, exception, _ = outcome
        self.write(f"  Test result:       {exception!r}\n")

    def write_section_header(self, section_title: str) -> None:
        """Write a section header, optionally including a subtest result header."""
        title_width = self.max_width - 10 - bool(self.verbosity) * 14
        section_title = self.fixed_width_text(section_title, width=title_width)
        if self.verbosity:
            section_title += "   P   F   T"

        self.writeln()
        self.write_separator("=")
        self.write(f"{section_title}\n")
        self.write_separator("=")


@dataclasses.dataclass
class SectionResults:
    """A class that holds summary results for a test class section of the test suite."""

    passed: int = 0
    failed: int = 0

    @property
    def total(self) -> int:
        """Get the total number of tests ran in this section."""
        return self.passed + self.failed

    def __iter__(self) -> typing.Iterator:
        """Iterate over the Section Results."""
        return iter((self.passed, self.failed, self.total))

    def __str__(self) -> str:
        """Create an end-user string representation of the section results."""
        return f"passed={self.passed:>3}, failed={self.failed:>3}, total={self.total:>3}"


class QualifierTestResult(unittest.TestResult):
    """A custom test result class used for testing entries for our Code Jam qualifier."""

    def __init__(
        self,
        stream: StreamWrapper = None,
        descriptions: typing.Optional[bool] = None,
        verbosity: typing.Optional[int] = None,
    ) -> None:
        super().__init__(stream.stream, descriptions, verbosity)
        self.verbosity = verbosity
        self.stream = stream
        self.current_testclass = None
        self.test_results = {}

    def get_description(self, callable_object: typing.Callable) -> str:
        """Extract a description from the callable by looking at the docstring."""
        if callable_object.__doc__:
            description = callable_object.__doc__.splitlines()[0].rstrip(".!?")
        else:
            description = str(callable_object)
        return description

    def switch_testclass(self, test: unittest.TestCase) -> None:
        """Switch to the new test class and print a section header."""
        self.current_testclass = type(test)
        self.test_results[self.current_testclass] = SectionResults()

        section_header = self.get_description(self.current_testclass)
        self.stream.write_section_header(section_header)

    def startTest(self, test: unittest.TestCase) -> None:
        """Prepare the test phase of an individual test method."""
        super().startTest(test)
        self.subtest_results = SectionResults()
        self.subtest_outcomes = []

        if type(test) != self.current_testclass:
            self.switch_testclass(test)

    def stopTest(self, test: unittest.TestCase) -> None:
        """Finalize the test phase of an individual test method."""
        test_description = test.shortDescription().rstrip(".!?")
        self.stream.write_test_description(test_description, self.subtest_results)

        if not self.subtest_outcomes:
            self.stream.writeln("[ PASS ]")
            self.test_results[self.current_testclass].passed += 1
        else:
            self.stream.writeln("[ FAIL ]")
            self.test_results[self.current_testclass].failed += 1

            if self.verbosity > 1:
                for subtest, outcome in self.subtest_outcomes:
                    self.stream.write_subtest_failure(subtest, outcome)

                self.stream.write_separator("-")
                self.stream.writeln()

    def addSubTest(
        self,
        test: unittest.TestCase,
        subtest: unittest.TestCase,
        outcome: typing.Optional[TestOutcome],
    ) -> None:
        """Process the result of a subTest."""
        super().addSubTest(test, subtest, outcome)
        if outcome:
            self.subtest_results.failed += 1
            self.subtest_outcomes.append((subtest, outcome))
            return

        self.subtest_results.passed += 1
