import argparse

from testsuite.runner import run_ascii_testsuite


parser = argparse.ArgumentParser(
    prog="python -m testsuite",
    description="Python Discord Code Jam: Qualifier Test Suite"
)
parser.set_defaults(ascii=False, verbosity=0)
subparsers = parser.add_subparsers(title="subcommands")
ascii_parser = subparsers.add_parser("ascii", help="testsuite ascii mode")
ascii_parser.add_argument(
    "--file",
    action="store",
    help="importable name of the file to test (default: qualifier)",
    default="qualifier",
)
ascii_parser.add_argument(
    "--verbose", "-v",
    action="count",
    help="verbosity of the output: '-v' or '-vv'",
    default=0,
    dest="verbosity",
)
ascii_parser.add_argument(
    "--outfile",
    action="store",
    help="file to write the output to (default: STDERR)",
    default="STDERR"
)
ascii_parser.set_defaults(ascii=True)
args = parser.parse_args()

if args.ascii:
    kwargs = vars(args)
    del kwargs['ascii']
    run_ascii_testsuite(**kwargs)

# if __name__ == "__main__":
#     test_suite = load_testsuite(test_qualifier, "qualifier")
#     runner = QualifierTestRunner(user="Ves Zappa", verbosity=2)
#     runner.run(test_suite)
