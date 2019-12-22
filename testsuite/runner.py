"""
This module holds the QualifierTestRunner and QualifierTestResult classes.

These classes are used to run a test suite against the qualifier solutions submitted by the members
of our server who would like to qualify for a place in a Code Jam.
"""
from __future__ import annotations

import datetime
import io
import sys
import textwrap
import timeit
import typing
import unittest

import test_qualifier

from testsuite.result import QualifierTestResult, StreamWrapper
from testsuite.testcase import load_testsuite


class QualifierTestRunner:
    """Test runner for our code jam qualifier test suite."""

    resultclass = QualifierTestResult

    def __init__(
        self,
        stream: typing.Optional[io.TextIOBase] = None,
        descriptions: bool = True,
        verbosity: int = 1,
        failfast: bool = False,
        buffer: bool = False,
        resultclass: typing.Optional[typing.Type[unittest.TestResult]] = None,
        title: str = "Python Discord Code Jam: Qualifier Test Suite",
        user: str = "",
        console_width: int = 100,
        *,
        tb_locals: bool = False,
    ) -> None:
        if stream is None:
            # By default, write to stderr. However, since stream accepts any
            # stream that implements the TextIOBase protocol, we could use this
            # parameter to write to file as well.
            stream = sys.stderr
        self.stream = StreamWrapper(stream, max_width=console_width, verbosity=verbosity)
        self.descriptions = descriptions
        self.verbosity = verbosity
        self.failfast = failfast
        self.buffer = False  # No support for buffered output at this point

        if resultclass is not None:
            self.resultclass = resultclass

        self.title = title
        self.user = user

    def instantiate_resultclass(self) -> unittest.TestResult:
        """Create an instance of the result class for a test run."""
        return self.resultclass(self.stream, self.descriptions, self.verbosity)

    def write_header(self) -> None:
        """Write a header for this test run."""
        self.stream.write_separator("=")
        self.stream.write(f"{self.title}\n")
        self.stream.write_separator("=")
        self.stream.writeln(
            f"Date: {datetime.datetime.utcnow().strftime(r'%Y-%m-%d %H:%M:%S')} UTC"
        )
        self.stream.writeln(f"User: {self.user}")
        self.stream.writeln()

    def write_footer(self, result: unittest.TestResult, duration: float) -> None:
        """Write a footer for this test run."""
        self.stream.writeln()
        self.stream.writeln()
        self.stream.write_separator("=")
        self.stream.writeln(f"Test Suite Summary")
        self.stream.write_separator("=")
        if hasattr(result, "test_results"):
            self.stream.write(
                f"{' '*30} PASSED   FAILED   TOTAL"
                "\n"
            )
            for section, section_results in result.test_results.items():
                section_name = section.__doc__.splitlines()[0].rstrip(".!?")
                section_name = textwrap.shorten(section_name, width=30, placeholder="...")
                self.stream.write(
                    f"{section_name:<30}  "
                    f"{section_results.passed:^6}   "
                    f"{section_results.failed:^6}  "
                    f"{section_results.total:^5}"
                    "\n"
                )
            self.stream.write_separator("-")
        self.stream.writeln(f"Total running time: {duration:.3f}s")

    def run(self, test: unittest.TestSuite) -> None:
        """Run a test suite containing `unittest.TestCase` tests."""
        result = self.instantiate_resultclass()
        self.write_header()

        # Record the start time
        start = timeit.default_timer()

        # Pass the TestResult instance to the test suite to run the tests
        test(result)

        # Record the end time
        duration = timeit.default_timer() - start
        self.write_footer(result, duration)


def run_ascii_testsuite(file: str, verbosity: int, outfile: str) -> None:
    """Run an ascii-based test suite."""
    stream = sys.stderr if outfile == "STDERR" else io.StringIO()
    test_suite = load_testsuite(test_qualifier, file)
    runner = QualifierTestRunner(user="Ves Zappa", verbosity=verbosity, stream=stream)
    runner.run(test_suite)
    if outfile != "STDERR":
        with open(outfile, "w", encoding="utf-8") as f:
            f.write(stream.getvalue())
        stream.close()
