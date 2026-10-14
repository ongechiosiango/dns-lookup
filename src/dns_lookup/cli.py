"""Command-line entry point for dns-lookup."""

from __future__ import annotations

import argparse
import sys

from rich.console import Console

from . import __version__
from .reporter import print_report, to_json
from .resolver import SUPPORTED_TYPES, LookupError, resolve

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dns-lookup",
        description="Query DNS records for a hostname and display them nicely.",
    )
    parser.add_argument("name", help="The domain name to look up (e.g. github.com).")
    parser.add_argument(
        "--type", "-t", action="append", default=None,
        help=f"Record type to query. Can be repeated. Choices: {', '.join(SUPPORTED_TYPES)}.",
    )
    parser.add_argument(
        "--timeout", type=float, default=5.0,
        help="Query timeout in seconds (default: 5).",
    )
    parser.add_argument(
        "--json", action="store_true", dest="as_json",
        help="Output results as JSON instead of a table.",
    )
    parser.add_argument("--version", action="version", version=f"dns-lookup {__version__}")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    types = [t.upper() for t in args.type] if args.type else None
    if types:
        invalid = [t for t in types if t not in SUPPORTED_TYPES]
        if invalid:
            console.print(f"[bold red]Error:[/bold red] unsupported type(s): {', '.join(invalid)}")
            console.print(f"Supported: {', '.join(SUPPORTED_TYPES)}")
            return 1

    try:
        results = resolve(args.name, record_types=types, timeout=args.timeout)
    except LookupError as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        return 1

    if args.as_json:
        print(to_json(args.name, results))
    else:
        print_report(args.name, results)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
