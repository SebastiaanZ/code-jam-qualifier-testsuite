"""
This module holds the QualifierTestRunner and QualifierTestResult classes.

These classes are used to run a test suite against the qualifier solutions submitted by the members
of our server who would like to qualify for a place in a Code Jam.
"""
from __future__ import annotations

import ast
import datetime
import io
import os
import pathlib
import re
import subprocess
import sys
import textwrap
import timeit
import typing
import unittest

import mccabe

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
        max_complexity: int = -1,
        flake8_report: str = "",
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

        self.max_complexity = max_complexity
        self.flake8_report = flake8_report

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
                f"{' '*30} PASSED   FAILED   TOTAL   RESULT"
                "\n"
            )
            for section, section_results in result.test_results.items():
                section_name = section.__doc__.splitlines()[0].rstrip(".!?")
                section_name = textwrap.shorten(section_name, width=30, placeholder="...")
                passed, failed, total = section_results
                result = "PASS" if passed == total else "FAIL"
                self.stream.write(
                    f"{section_name:<30}  "
                    f"{passed:^6}   "
                    f"{failed:^6}  "
                    f"{total:^5}    "
                    f"{result}"
                    "\n"
                )
            self.stream.write_separator("-")

        self.stream.write(f"Maximum McCabe Complexity: {self.max_complexity:>2d}\n")

        flake8_errors = len(self.flake8_report.splitlines())
        self.stream.write(f"Number of flake8 errors:   {flake8_errors:>2d}\n")
        if self.verbosity > 1:
            self.stream.writeln("Flake8 Report:")
            self.stream.write(textwrap.indent(self.flake8_report, prefix="  "))

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


def get_max_mccabe_complexity(path: pathlib.Path) -> int:
    """Calculate the maximum McCabe Complexity for this file."""
    with path.open("r", encoding="utf-8") as f:
        code = f.read()

    try:
        tree = compile(code, path, "exec", ast.PyCF_ONLY_AST)
    except SyntaxError:
        return -1

    mccabe.McCabeChecker.max_complexity = 0
    complexity = re.compile(r"\((?P<complexity>\d+)\)")
    max_complexity = max(
        int(complexity.search(text)["complexity"])
        for _, _, text, _ in mccabe.McCabeChecker(tree, path).run()
    )
    return max_complexity


def run_ascii_testsuite(file: str, verbosity: int, outfile: str) -> None:
    """Run an ascii-based test suite."""
    stream = sys.stderr if outfile == "STDERR" else io.StringIO()

    path = file.split(".")
    path[-1] += ".py"
    path = pathlib.Path(*path)

    max_complexity = get_max_mccabe_complexity(path)
    flake8_report = subprocess.check_output(
        ["pipenv", "run", "flake8", "--exit-zero", "--select", "E,F,W", "--max-line-length", "10", str(path)],
        cwd=os.getcwd(),
        stderr=subprocess.STDOUT,
        encoding="utf-8"
    )

    test_suite = load_testsuite(test_qualifier, file)
    runner = QualifierTestRunner(
        user="Ves Zappa",
        verbosity=verbosity,
        stream=stream,
        max_complexity=max_complexity,
        flake8_report=flake8_report,
    )
    runner.run(test_suite)

    if outfile != "STDERR":
        with open(outfile, "w", encoding="utf-8") as f:
            f.write(stream.getvalue())
        stream.close()
