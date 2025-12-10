import argparse
import sys

from .notebook import ColabLinter


def handle_check(args):
    """colablinter check'"""
    linter = ColabLinter()
    linter.check()


def main():
    parser = argparse.ArgumentParser(
        description="Colablinter: A utility for linting and formatting Colab notebooks."
    )

    subparsers = parser.add_subparsers(title="subcommands")

    parser_check = subparsers.add_parser(
        "check", help="Checks Colab notebooks for issues."
    )
    parser_check.set_defaults(func=handle_check)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
