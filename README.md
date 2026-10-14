# DNS Lookup

[![CI](https://github.com/ongechiosiango/dns-lookup/actions/workflows/ci.yml/badge.svg)](https://github.com/ongechiosiango/dns-lookup/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

A command-line DNS lookup tool with rich terminal output.

## Features

- Resolves A, AAAA, CNAME, MX, NS, TXT, and SOA records.
- Pretty rich tables, one per record type.
- JSON output for scripting.
- Per-query timeout configuration.
- Deterministic tests using an injectable resolver (no live DNS in CI).

## Installation

From source:

    git clone git@github.com:ongechiosiango/dns-lookup.git
    cd utility-tool-7
    python3 -m venv venv
    source venv/bin/activate
    pip install -e ".[dev]"

## Usage

    dns-lookup github.com

Only specific types:

    dns-lookup github.com -t A -t MX

JSON output:

    dns-lookup github.com --json

See docs/usage.md for more.

## Development

    pip install -e ".[dev]"
    pytest -v

## Contributing

See CONTRIBUTING.md.

## License

MIT - see LICENSE.
